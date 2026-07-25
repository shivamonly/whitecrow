from ..core.client import fetch
from concurrent.futures import ThreadPoolExecutor, as_completed

PATHS = [
    # admin / auth
    "/admin", "/admin/", "/admin.php", "/admin/login", "/admin/panel",
    "/login", "/login.php", "/signup", "/register", "/forgot",
    "/forgot-password", "/reset-password", "/2fa", "/otp", "/verify",
    "/logout", "/session",

    # config & secrets
    "/.git/config", "/.git/HEAD", "/.gitignore", "/.gitattributes",
    "/.env", "/.env.example", "/.env.prod", "/.env.staging",
    "/.env.local", "/.svn", "/.svn/entries", "/.DS_Store",
    "/.htaccess", "/.htpasswd", "/config", "/config.php",
    "/config.json", "/config.xml", "/configuration.php",
    "/database.yml", "/database.json", "/db.php",
    "/settings", "/settings.php", "/settings.json",
    "/appsettings.json", "/app.config", "/web.config",
    "/connectionstrings", "/connectionstrings.xml",
    "/parameters.xml", "/parameters.yml",

    # cms paths
    "/wp-admin", "/wp-admin/", "/wp-login.php", "/wp-content",
    "/wp-content/", "/wp-content/themes/", "/wp-content/plugins/",
    "/wp-content/uploads/", "/wp-includes", "/wp-config.php",
    "/wp-json/", "/wp-cron.php", "/xmlrpc.php",
    "/administrator", "/administrator/", "/components/",
    "/modules/", "/plugins/", "/templates/",
    "/joomla.xml", "/Joomla.xml",
    "/sites/default/files/", "/sites/default/settings.php",
    "/drupal", "/Drupal",

    # api endpoints
    "/api", "/api/", "/api/v1", "/api/v1/", "/api/v2", "/api/v2/",
    "/api/v3", "/api/health", "/api/status", "/api/version",
    "/api/user", "/api/users", "/api/admin", "/api/login",
    "/api/auth", "/api/token", "/api/register", "/api/search",
    "/api/upload", "/api/download", "/api/export", "/api/import",
    "/api/config", "/api/settings", "/api/keys", "/api/docs",
    "/swagger", "/swagger/", "/swagger.json", "/swagger.yaml",
    "/swagger-ui", "/swagger-ui/", "/api-docs", "/api-docs/",
    "/openapi.json", "/openapi.yaml", "/graphql",
    "/graphql/", "/api/graphql", "/api/graphql/",
    "/rest", "/rest/", "/soap", "/soap/",
    "/api/swagger", "/api/swagger.json",

    # dev / staging
    "/dev", "/dev/", "/staging", "/staging/", "/beta", "/beta/",
    "/test", "/test/", "/testing", "/testing/", "/demo", "/demo/",
    "/sandbox", "/sandbox/", "/stage", "/stage/", "/preview",
    "/internal", "/internal/", "/private", "/private/",
    "/backup", "/backup/", "/old", "/old/", "/new", "/new/",
    "/temp", "/temp/", "/tmp", "/tmp/",
    "/phpmyadmin", "/phpmyadmin/", "/phpMyAdmin", "/pma",
    "/adminer", "/adminer/", "/phpPgAdmin",

    # files & uploads
    "/uploads", "/uploads/", "/upload", "/upload/",
    "/files", "/files/", "/download", "/download/",
    "/assets", "/assets/", "/static", "/static/",
    "/media", "/media/", "/images", "/images/",
    "/backup.sql", "/database.sql", "/dump.sql", "/db.sql",
    "/backup.zip", "/backup.tar", "/backup.gz",
    "/database_backup.sql", "/mysql_backup.sql",

    # debug / info
    "/info.php", "/phpinfo.php", "/test.php", "/debug",
    "/debug/", "/error", "/error/", "/error.log",
    "/server-status", "/server-info", "/info",
    "/actuator", "/actuator/", "/actuator/health",
    "/actuator/info", "/actuator/beans", "/actuator/env",
    "/actuator/mappings", "/actuator/metrics",
    "/actuator/trace", "/actuator/dump",
    "/heapdump", "/heapdump.json",
    "/metrics", "/prometheus",

    # security files
    "/robots.txt", "/sitemap.xml", "/sitemap_index.xml",
    "/crossdomain.xml", "/clientaccesspolicy.xml",
    "/security.txt", "/.well-known/security.txt",
    "/.well-known/openid-configuration",
    "/.well-known/assetlinks.json",
    "/.well-known/apple-app-site-association",
    "/humans.txt", "/ads.txt",

    # source & packages
    "/package.json", "/package-lock.json",
    "/yarn.lock", "/pnpm-lock.yaml",
    "/composer.json", "/composer.lock",
    "/Gemfile", "/Gemfile.lock",
    "/Makefile", "/Dockerfile", "/docker-compose.yml",
    "/docker-compose.yaml", "/Dockerfile.prod",
    "/requirements.txt", "/Pipfile", "/Pipfile.lock",
    "/setup.py", "/pyproject.toml",
    "/pom.xml", "/build.gradle", "/gradle.properties",
    "/README.md", "/CHANGELOG.md", "/LICENSE",
    "/terraform.tfstate", "/terraform.tfvars",
    "/serverless.yml", ".serverless.yml",
    "/webpack.config.js", "/vite.config.js",
    "/babel.config.js", "/tsconfig.json",

    # common app paths
    "/dashboard", "/dashboard/", "/home", "/home/",
    "/index", "/index.html", "/index.php",
    "/search", "/search/", "/sitemap",
    "/contact", "/contact/", "/about", "/about/",
    "/help", "/help/", "/faq", "/faq/",
    "/terms", "/privacy", "/policy",
    "/newsletter", "/subscribe", "/unsubscribe",
    "/webhook", "/webhooks", "/callback",
    "/profile", "/profile/", "/account", "/account/",
    "/cart", "/cart/", "/checkout", "/checkout/",
    "/order", "/orders", "/invoice",
    "/notifications", "/notification",
    "/cron", "/cron.php", "/cron-job",
    "/proxy", "/proxy/", "/redirect",
    "/tracking", "/track", "/analytics",

    # Cloud / hosting
    "/.aws", "/.aws/credentials", "/.aws/config",
    "/.azure", "/.gcp",
    "/.s3", "/s3", "/bucket",
    "/.cloudfront", "/cloudfront",
    "/firebase.json", "/.firebaserc",
    "/.circleci", "/.circleci/config.yml",
    "/.travis.yml", "/.github", "/.github/workflows",
    "/Jenkinsfile", "/.jenkins",

    # api keys & tokens
    "/.npmrc", "/.yarnrc",
    "/.env.production", "/.env.development",
    "/.secret", "/secrets", "/secrets.yml",
    "/key", "/keys", "/apikey", "/api-key",
    "/token", "/tokens",

    # version control
    "/.hg", "/.bzr",
    "/.idea", "/.vscode",
    "/.project", "/.classpath",
    "/.settings", "/.buildpath",
]


def discover(url):
    base = url.rstrip("/")
    found = []

    def _check(path):
        u = f"{base}{path}"
        try:
            s, h, b = fetch(u, timeout=4)
            if s and s not in (404, 400):
                ct = h.get("Content-Type", "")
                return {"url": u, "status": s, "size": len(b), "type": ct}
        except Exception:
            pass
        return None

    with ThreadPoolExecutor(max_workers=25) as ex:
        futures = {ex.submit(_check, p): p for p in PATHS}
        for f in as_completed(futures):
            r = f.result()
            if r:
                found.append(r)

    found.sort(key=lambda x: x["status"])
    return found
