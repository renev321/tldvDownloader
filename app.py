import re
import json
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st


st.set_page_config(page_title="tl;dv Downloader", page_icon="🎥", layout="centered")

st.title("🎥 tl;dv Meeting Downloader")
st.caption("Paste your tl;dv meeting URL and authorization token.")

st.warning(
    "Use this only for meetings you own or have permission to download. "
    "Do not share your authorization token publicly."
)


def sanitize_filename(text: str) -> str:
    text = re.sub(r'[\\/*?:"<>|]', "_", text)
    return text.strip()[:120] or "tldv_meeting"


def extract_meeting_id(url: str) -> str:
    clean_url = url.strip().rstrip("/")
    return clean_url.split("/")[-1]


def get_meeting_data(meeting_id: str, auth_token: str) -> dict:
    api_url = f"https://gw.tldv.io/v1/meetings/{meeting_id}/watch-page?noTranscript=true"

    response = requests.get(
        api_url,
        headers={"Authorization": auth_token.strip()},
        timeout=30,
    )

    response.raise_for_status()
    return response.json()


def download_video(video_url: str, output_path: Path):
    command = [
        "ffmpeg",
        "-y",
        "-i",
        video_url,
        "-c",
        "copy",
        str(output_path),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr)


with st.expander("How to get the auth token"):
    st.markdown(
        """
        1. Open tl;dv and log in.  
        2. Open the meeting page.  
        3. Open Developer Tools with F12.  
        4. Go to the Network tab and refresh the page.  
        5. Find the request similar to:  
           `https://gw.tldv.io/v1/meetings/.../watch-page?noTranscript=true`  
        6. Copy the `Authorization` request header value.  
        7. Paste it below.
        """
    )

meeting_url = st.text_input("tl;dv meeting URL")
auth_token = st.text_area("Authorization token", type="password", height=100)

if st.button("Download meeting", type="primary"):
    if not meeting_url or not auth_token:
        st.warning("Please paste both the meeting URL and auth token.")
        st.stop()

    try:
        meeting_id = extract_meeting_id(meeting_url)
        st.info(f"Meeting ID found: {meeting_id}")

        data = get_meeting_data(meeting_id, auth_token)

        meeting = data.get("meeting", {})
        name = meeting.get("name", "No name")
        created_at = meeting.get("createdAt")
        source = data.get("video", {}).get("source")

        if not source:
            st.error("No video source found. Check the token or meeting URL.")
            st.stop()

        if created_at:
            date = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            date = datetime.now()

        normalised_date = date.strftime("%Y-%m-%d-%H-%M-%S")
        filename = sanitize_filename(f"{normalised_date}_{name}.mp4")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / filename

            with st.spinner("Downloading video..."):
                download_video(source, output_path)

            video_bytes = output_path.read_bytes()

            st.success("Video ready!")

            st.download_button(
                label="⬇️ Download MP4",
                data=video_bytes,
                file_name=filename,
                mime="video/mp4",
            )

            st.download_button(
                label="⬇️ Download JSON metadata",
                data=json.dumps(data, indent=2),
                file_name=filename.replace(".mp4", ".json"),
                mime="application/json",
            )

    except requests.HTTPError as e:
        st.error(f"Request failed: {e}")
    except Exception as e:
        st.error(f"Error: {e}")
