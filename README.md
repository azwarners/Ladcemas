# Ladcemas

Ladcemas is a planned installer and orchestration interface for self-hosted applications. **Ladcemas-Lite** is its first working slice: a small, read-only Flask page with links to the installed web applications recorded in Aggregare's deployment report.

## Run Ladcemas-Lite

Use the same unprivileged account that owns the Aggregare report. Aggregare protects the report because it can contain initial login credentials.

```sh
cd Ladcemas
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python app.py
```

By default the server listens only on localhost; open <http://127.0.0.1:5000> on the Aggregare host. To make it reachable over the LAN, bind on all interfaces:

```sh
LADCEMAS_HOST=0.0.0.0 python app.py
```

Then open `http://<aggregare-server-lan-address>:5000` from a LAN device. Configure the host firewall as needed. `LADCEMAS_HOST` controls where Flask listens; it does not change the application links. Those links come from the URLs in Aggregare's report, so Aggregare should be configured to record endpoints reachable by the intended browsers (localhost for local-only use, or the server's LAN address for LAN use).

By default, the report is read from `/var/lib/aggregare/deployment-report.md`; override the path with `AGGREGARE_REPORT_PATH` if needed. Set `LADCEMAS_PORT` to change the listening port.

The page reads the report on each request, so refreshing after Aggregare regenerates the report updates the links. It displays installed user-facing applications with a recorded HTTP(S) endpoint, converts known health-check URLs to the application root, and omits Apmatia and Ysparr because they do not provide a user-facing launcher destination. It does not install, configure, or manage applications.

## Project direction

The long-term goal is a Linux desktop application with broader installation and lifecycle functionality. Ladcemas-Lite starts with a web-friendly feature: launching the self-hosted apps installed on Aggregare Server.
