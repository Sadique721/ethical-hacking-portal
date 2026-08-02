import os
import time
import httpx
from datetime import datetime
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.cache import cache
from django.http import FileResponse, HttpResponse
from .tasks import generate_pdf_report_task

# ──────────────────────────────────────────────────────────────────────────────
# Fallback Offline CVE Database (prevents rate-limit issues during demos)
# ──────────────────────────────────────────────────────────────────────────────
def get_fallback_cves(query):
    fallback_database = [
        {
            "id": "CVE-2021-44228",
            "description": "Apache Log4j2 2.0-beta9 through 2.15.0 JNDI features used in configuration, log messages, and parameters do not protect against attacker controlled LDAP and other JNDI related endpoints.",
            "score": "10.0",
            "severity": "CRITICAL"
        },
        {
            "id": "CVE-2017-0144",
            "description": "The SMBv1 server in Microsoft Windows allows remote attackers to execute arbitrary code via crafted packets, aka 'EternalBlue'.",
            "score": "8.1",
            "severity": "HIGH"
        },
        {
            "id": "CVE-2014-0160",
            "description": "The TLS/DTLS implementations in OpenSSL 1.0.1 before 1.0.1g do not properly handle Heartbeat Extension packets, allowing remote attackers to obtain sensitive information from process memory, aka 'Heartbleed'.",
            "score": "7.5",
            "severity": "HIGH"
        },
        {
            "id": "CVE-2023-38606",
            "description": "An issue was addressed with improved state management in Apple iOS, iPadOS, macOS, watchOS, and tvOS. A malicious app may be able to modify sensitive kernel state.",
            "score": "7.8",
            "severity": "HIGH"
        },
        {
            "id": "CVE-2024-3094",
            "description": "Malicious code was discovered in the XZ Utils library versions 5.6.0 and 5.6.1, allowing unauthorized remote access by exploiting SSH authentication mechanisms.",
            "score": "10.0",
            "severity": "CRITICAL"
        }
    ]
    query_lower = query.lower()
    return [c for c in fallback_database if query_lower in c["id"].lower() or query_lower in c["description"].lower()]


# ──────────────────────────────────────────────────────────────────────────────
# CVE Lookup View (sync – compatible with WSGI & ASGI)
# ──────────────────────────────────────────────────────────────────────────────
def cve_lookup(request):
    query = request.GET.get('query', '').strip()
    results = []
    error = None

    if query:
        cache_key = f"cve_search_{query}"
        cached_data = cache.get(cache_key)

        if cached_data:
            results = cached_data
        else:
            url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
            params = {}
            if query.upper().startswith("CVE-"):
                params["cveId"] = query.upper()
            else:
                params["keywordSearch"] = query

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
                            desc_text = next(
                                (d.get("value") for d in descriptions if d.get("lang") == "en"),
                                "No description available."
                            )
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
                        cache.set(cache_key, results, 86400)  # Cache for 24h
                    else:
                        results = get_fallback_cves(query)
                        error = f"NVD API returned status {response.status_code}. Serving offline database matches."
            except Exception:
                results = get_fallback_cves(query)
                error = "NVD API timed out or rate limit reached. Serving offline database matches."

    context = {'query': query, 'results': results, 'error': error}
    if request.headers.get('HX-Request'):
        return render(request, 'utilities/cve_results_partial.html', context)
    return render(request, 'utilities/cve_lookup.html', context)


# ──────────────────────────────────────────────────────────────────────────────
# HTTP Security Header Analyzer View (sync – compatible with WSGI & ASGI)
# ──────────────────────────────────────────────────────────────────────────────
def header_analyzer(request):
    target_url = request.GET.get('url', '').strip()
    results = None
    error = None

    if target_url:
        url = target_url
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url

        try:
            with httpx.Client(timeout=5.0, follow_redirects=True) as client:
                response = client.get(url, headers={'User-Agent': 'Mozilla/5.0 (Security Scanner)'})
                headers = response.headers

                analyzed = {
                    "csp": {
                        "name": "Content-Security-Policy",
                        "present": "Content-Security-Policy" in headers,
                        "value": headers.get("Content-Security-Policy", "Not Set"),
                        "description": "Defends against XSS and injection attacks by whitelisting trusted sources of scripts/styles."
                    },
                    "xfo": {
                        "name": "X-Frame-Options",
                        "present": "X-Frame-Options" in headers,
                        "value": headers.get("X-Frame-Options", "Not Set"),
                        "description": "Guards against Clickjacking by ensuring browsers do not frame your page."
                    },
                    "hsts": {
                        "name": "Strict-Transport-Security",
                        "present": "Strict-Transport-Security" in headers,
                        "value": headers.get("Strict-Transport-Security", "Not Set"),
                        "description": "Enforces TLS/HTTPS connections, mitigating man-in-the-middle attacks."
                    },
                    "nosniff": {
                        "name": "X-Content-Type-Options",
                        "present": "X-Content-Type-Options" in headers,
                        "value": headers.get("X-Content-Type-Options", "Not Set"),
                        "description": "Instructs browsers to respect declared Content-Types, blocking MIME sniffing."
                    },
                    "referrer": {
                        "name": "Referrer-Policy",
                        "present": "Referrer-Policy" in headers,
                        "value": headers.get("Referrer-Policy", "Not Set"),
                        "description": "Governs how much information is leaked in the HTTP Referer header when navigating."
                    }
                }

                # Grade calculation
                points = 0
                if analyzed["csp"]["present"]:     points += 30
                if analyzed["xfo"]["present"]:     points += 20
                if analyzed["hsts"]["present"]:    points += 20
                if analyzed["nosniff"]["present"]: points += 15
                if analyzed["referrer"]["present"]: points += 15

                if points >= 90:   grade = "A+"
                elif points >= 80: grade = "A"
                elif points >= 70: grade = "B"
                elif points >= 50: grade = "C"
                elif points >= 30: grade = "D"
                else:              grade = "F"

                results = {
                    "url": url,
                    "score": points,
                    "grade": grade,
                    "headers": analyzed,
                    "raw_headers": dict(headers)
                }
        except Exception as e:
            error = f"Connection failed to {url}. (Details: {str(e)})"

    context = {'url': target_url, 'results': results, 'error': error}
    if request.headers.get('HX-Request'):
        return render(request, 'utilities/header_results_partial.html', context)
    return render(request, 'utilities/header_analyzer.html', context)


# ──────────────────────────────────────────────────────────────────────────────
# PDF Pentest Report Generator
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def generate_report(request):
    if request.method == "POST":
        title = request.POST.get('title', '').strip()
        severity = request.POST.get('severity', 'Medium')
        cvss_score = request.POST.get('cvss_score', '5.0')
        description = request.POST.get('description', '').strip()
        impact = request.POST.get('impact', '').strip()
        remediation = request.POST.get('remediation', '').strip()

        if not title or not description:
            messages.error(request, "Vulnerability Title and Description are required.")
            return redirect('generate_report')

        # Ensure media directory exists
        reports_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
        os.makedirs(reports_dir, exist_ok=True)

        filename = f"report_{request.user.id}_{int(time.time())}.pdf"
        filepath = os.path.join(reports_dir, filename)

        # Enqueue background task (runs synchronously on ImmediateBackend)
        generate_pdf_report_task.enqueue(
            title=title,
            severity=severity,
            cvss_score=cvss_score,
            description=description,
            impact=impact,
            remediation=remediation,
            filepath=filepath
        )

        # Serve the generated PDF immediately for download
        if os.path.exists(filepath):
            response = FileResponse(open(filepath, 'rb'), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Security_Pentest_Report_{datetime.now().strftime("%Y%m%d")}.pdf"'
            return response
        else:
            messages.error(request, "Failed to compile the PDF report.")

    return render(request, "utilities/report_generator.html")
