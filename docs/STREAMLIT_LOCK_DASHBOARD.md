# Streamlit Dashboard Usage

1. **Install dependencies** (if not already):
   ```bash
   pip install streamlit
   ```

2. **Launch** using helper script:
   ```bash
   python scripts/launch_lock_dashboard.py
   # or specify a port
   python scripts/launch_lock_dashboard.py --port 8502
   ```

3. **Access** the dashboard in the browser at `http://localhost:<port>`.

4. **Stop** the dashboard with `Ctrl+C`. The CLI fallback command remains:
   ```bash
   python scripts/lock_dashboard.py --agent <you> --files <paths>
   ```

5. Include a screenshot or summary link in the handoff report if useful for the next agent.
- 기존 Streamlit UI(streamlit_app.py) 사이드바에서 Lock Dashboard 링크(기본 포트 8502)와 실행 명령을 확인할 수 있습니다.
