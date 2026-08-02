import httpx
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from django.core.cache import cache
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from MSA.models import Profile
from MSA.serializers import UserSerializer
from ctf.models import Challenge, Submission
from ctf.serializers import ChallengeSerializer, SubmissionSerializer
from utilities.views import get_fallback_cves

class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to list and retrieve security researcher profiles.
    """
    queryset = User.objects.filter(is_active=True).select_related('profile')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ChallengeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to list and retrieve CTF challenges.
    """
    queryset = Challenge.objects.all().order_by('points')
    serializer_class = ChallengeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @extend_schema(
        request=SubmissionSerializer,
        responses={201: SubmissionSerializer, 400: OpenApiTypes.STR},
        description="Submit a flag attempt for a specific challenge."
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def submit_flag(self, request, pk=None):
        challenge = self.get_object()
        flag = request.data.get('submitted_flag', '').strip()
        
        if not flag:
            return Response({"error": "submitted_flag is required."}, status=status.HTTP_400_BAD_REQUEST)
            
        # Check if already solved
        already_solved = Submission.objects.filter(
            user=request.user, 
            challenge=challenge, 
            is_correct=True
        ).exists()
        
        if already_solved:
            return Response({"message": "Challenge already solved!"}, status=status.HTTP_400_BAD_REQUEST)
            
        submission = Submission.objects.create(
            user=request.user,
            challenge=challenge,
            submitted_flag=flag
        )
        
        serializer = SubmissionSerializer(submission)
        if submission.is_correct:
            return Response({
                "message": f"Correct flag! Points added: +{challenge.points}",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "message": "Incorrect flag attempt.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)


class CVESearchView(APIView):
    """
    API endpoint to search vulnerabilities in the NVD CVE database.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter("query", OpenApiTypes.STR, OpenApiParameter.QUERY, required=True, description="CVE ID or keyword")
        ],
        description="Search vulnerability data from the NVD database (cached for 24h)."
    )
    def get(self, request):
        query = request.query_params.get('query', '').strip()
        if not query:
            return Response({"error": "query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
            
        cache_key = f"cve_search_api_{query}"
        cached_results = cache.get(cache_key)
        
        if cached_results:
            return Response(cached_results)
            
        # Execute query synchronous or wrapper (DRF views are synchronous, which is fine)
        url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        params = {}
        if query.upper().startswith("CVE-"):
            params["cveId"] = query.upper()
        else:
            params["keywordSearch"] = query
            
        results = []
        try:
            with httpx.Client(timeout=4.0) as client:
                response = client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    vulnerabilities = data.get("vulnerabilities", [])
                    for v in vulnerabilities[:10]:
                        cve_data = v.get("cve", {})
                        cve_id = cve_data.get("id", "N/A")
                        descriptions = cve_data.get("descriptions", [])
                        desc_text = next((d.get("value") for d in descriptions if d.get("lang") == "en"), "")
                        
                        metrics = cve_data.get("metrics", {})
                        cvss_v3 = metrics.get("cvssMetricV31", []) or metrics.get("cvssMetricV30", [])
                        base_score = "N/A"
                        severity = "UNKNOWN"
                        if cvss_v3:
                            cvss_data = cvss_v3[0].get("cvssData", {})
                            base_score = cvss_data.get("baseScore", "N/A")
                            severity = cvss_data.get("baseSeverity", "UNKNOWN")
                            
                        results.append({
                            "id": cve_id,
                            "description": desc_text,
                            "score": base_score,
                            "severity": severity
                        })
                    cache.set(cache_key, results, 86400)
                    return Response(results)
        except Exception:
            pass
            
        # Fallback to local offline cache
        results = get_fallback_cves(query)
        return Response({
            "warning": "Live NVD API request failed. Loaded cached database.",
            "results": results
        })


class HeaderAnalyzerView(APIView):
    """
    API endpoint to audit HTTP response security headers.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter("url", OpenApiTypes.STR, OpenApiParameter.QUERY, required=True, description="Target host URL")
        ],
        description="Audits the security headers of a target URL and calculates a security grade."
    )
    def get(self, request):
        target_url = request.query_params.get('url', '').strip()
        if not target_url:
            return Response({"error": "url parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
            
        url = target_url
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url
            
        try:
            with httpx.Client(timeout=4.0, follow_redirects=True) as client:
                response = client.get(url, headers={'User-Agent': 'Mozilla/5.0 (Security Scanner)'})
                headers = response.headers
                
                analyzed = {
                    "csp": "Content-Security-Policy" in headers,
                    "xfo": "X-Frame-Options" in headers,
                    "hsts": "Strict-Transport-Security" in headers,
                    "nosniff": "X-Content-Type-Options" in headers,
                    "referrer": "Referrer-Policy" in headers
                }
                
                points = 0
                if analyzed["csp"]: points += 30
                if analyzed["xfo"]: points += 20
                if analyzed["hsts"]: points += 20
                if analyzed["nosniff"]: points += 15
                if analyzed["referrer"]: points += 15
                
                if points >= 90: grade = "A+"
                elif points >= 80: grade = "A"
                elif points >= 70: grade = "B"
                elif points >= 50: grade = "C"
                elif points >= 30: grade = "D"
                else: grade = "F"
                
                return Response({
                    "target_url": url,
                    "score": points,
                    "grade": grade,
                    "security_headers": analyzed,
                    "raw_headers": dict(headers)
                })
        except Exception as e:
            return Response({"error": f"Failed to establish connection to target. {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
