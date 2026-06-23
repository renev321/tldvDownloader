# tl;dv Downloader Streamlit App

A simple Streamlit app to download tl;dv meeting videos using a meeting URL and authorization token.

## Important

Use this only for meetings you own or have permission to download. Never publish your authorization token.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

You also need ffmpeg installed and available in your PATH.

## Deploy to Streamlit Community Cloud

1. Upload this folder to a GitHub repository.
2. Go to Streamlit Community Cloud.
3. Select the repository.
4. Set the main file as `app.py`.
5. Deploy.

The `packages.txt` file tells Streamlit Cloud to install ffmpeg.
