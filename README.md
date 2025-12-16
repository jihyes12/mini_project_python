# mini_project_python

# Streamlit Arcade Shooter (1-Minute Survival)

본 프로젝트는 대한민국 오락실 감성의 **세로 스크롤 슈팅 게임**을 Python과 Streamlit을 이용해 구현한 과제용 프로젝트입니다.
플레이어는 키보드로 비행기를 조작하며, **10초 동안 생존하면 게임을 클리어**하는 구조입니다.

---

# 프로젝트 개요

* 장르: 세로 스크롤 아케이드 슈팅 게임
* 플레이 시간: 10초 (고정)
* 목표: 적 비행기 및 적 탄과 충돌하지 않고 생존
* 특징: Python(Streamlit) + JavaScript(Canvas) 연동

---

# 조작 방법

* 방향키 (← ↑ → ↓): 이동
* Q 키: 단발 공격
* W 키: 스프레드 공격

---

# 기술 스택

* Python 3.x
* Streamlit (웹 UI 및 실행 환경)
* JavaScript (Canvas, requestAnimationFrame 기반 게임 로직)
* streamlit.components.html (iframe 렌더링)

---

# 프로젝트 구조

```
project/
 ├─ main.py    # Streamlit 엔트리 포인트
 └─ README.md  # 프로젝트 설명
```

---

# 실행 방법

## 공통 사항

* Python 3.9 이상 권장
* Streamlit 설치 필요

---

## macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install streamlit
python -m streamlit run main.py
```

---

## Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install streamlit
python -m streamlit run main.py
```

브라우저가 자동으로 열리며, 열리지 않을 경우 아래 주소로 접속합니다.

```
http://localhost:8501
```

---

# 구현 방식 요약

* Streamlit을 이용해 Python 기반 웹 애플리케이션 실행
* HTML + JavaScript(Canvas)를 iframe으로 삽입하여 게임 화면 렌더링
* JavaScript에서 게임 루프, 충돌 판정, 타이머 처리
* 10초 생존 시 Clear, 충돌 시 Game Over

---

# 참고 사항

* Streamlit iframe 특성상 게임 화면을 한 번 클릭해야 키 입력이 정상 동작할 수 있습니다.
* 본 프로젝트는 학습 목적의 학교 과제용 프로젝트입니다.

---

# 시연 영상



https://github.com/user-attachments/assets/2621ae3c-b740-4df0-8cf4-b67c347a8d16


