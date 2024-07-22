<p><a target="_blank" href="https://app.eraser.io/workspace/LQCcXFqJOypzDrun3YnZ" id="edit-in-eraser-github-link"><img alt="Edit in Eraser" src="https://firebasestorage.googleapis.com/v0/b/second-petal-295822.appspot.com/o/images%2Fgithub%2FOpen%20in%20Eraser.svg?alt=media&amp;token=968381c8-a7e7-472a-8ed6-4a6626da5501"></a></p>

<h1 align="center"><a href="https://github.com/ronknight/alibaba-open-api">Alibaba Open API Integration</a></h1>
<h4 align="center">A Python-based integration for the Alibaba Open API, providing authentication, token management, and product listing functionalities.
</h4>
<p align="center">
<a href="https://twitter.com/PinoyITSolution"><img src="https://img.shields.io/twitter/follow/PinoyITSolution?style=social"></a>
<a href="https://github.com/ronknight?tab=followers"><img src="https://img.shields.io/github/followers/ronknight?style=social"></a>
<a href="https://github.com/ronknight/ronknight/stargazers"><img src="https://img.shields.io/github/stars/BEPb/BEPb.svg?logo=github"></a>
<a href="https://github.com/ronknight/ronknight/network/members"><img src="https://img.shields.io/github/forks/BEPb/BEPb.svg?color=blue&logo=github"></a>
  <a href="https://youtube.com/@PinoyITSolution"><img src="https://img.shields.io/youtube/channel/subscribers/UCeoETAlg3skyMcQPqr97omg"></a>
<a href="https://github.com/ronknight/alibaba-open-api/issues"><img src="https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat"></a>
<a href="https://github.com/ronknight/alibaba-open-api/blob/master/LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
<a href="#"><img src="https://img.shields.io/badge/Made%20with-Python-1f425f.svg"></a>
<a href="https://github.com/ronknight"><img src="https://img.shields.io/badge/Made%20with%20%F0%9F%A4%8D%20by%20-%20Ronknight%20-%20red"></a>
</p>
<p align="center">
  <a href="#requirements">Requirements</a> •
  <a href="#usage">Usage</a> •
  <a href="#scripts">Scripts</a> •
  <a href="#disclaimer">Disclaimer</a> •
  <a href="#diagrams">Diagrams</a> •
</p>

---

## 📋 Requirements

To run this project, you need:

- Python 3.7+
- pip (Python package installer)

Required Python packages:

```
anyio==4.4.0
argon2-cffi==23.1.0
requests==2.32.3
python-dotenv==1.0.1
```

A full list of dependencies can be found in the `requirements.txt` file.

## 🚀 Usage

1. Clone the repository:
   ```
   git clone https://github.com/ronknight/alibaba-open-api.git
   cd alibaba-open-api
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your `.env` file with the necessary credentials:
   ```
   APP_KEY=your_app_key
   APP_SECRET=your_app_secret
   REDIRECT_URI=your_redirect_uri
   ```

4. Run the scripts in the following order:
   ```
   python 1initiate.py
   python 2createtoken.py
   python 3refreshtoken.py
   python productlist.py
   ```

## 📜 Scripts

1. `1initiate.py`: Initiates the OAuth process and obtains the authorization code.
2. `2createtoken.py`: Creates access and refresh tokens using the authorization code.
3. `3refreshtoken.py`: Refreshes the access token using the refresh token.
4. `productlist.py`: Retrieves the product list using the access token.

Each script performs a specific function in the API integration process, from authentication to data retrieval.

## ⚠️ Disclaimer

This project is for educational purposes only. Ensure you comply with Alibaba's API usage terms and conditions.

<!-- eraser-additional-content -->
## 📊 Diagrams
<!-- eraser-additional-files -->
<a href="/README-Alibaba Open API Integration-2.eraserdiagram" data-element-id="0BmuCW_bBbA32G5-fmgNS"><img src="/.eraser/LQCcXFqJOypzDrun3YnZ___3Jivg2tjMecMlrHwbIVIBR8f7U03___---diagram----6c7c2e2c9f3e61576818dea1e6cfcf11-Alibaba-Open-API-Integration.png" alt="" data-element-id="0BmuCW_bBbA32G5-fmgNS" /></a>
<a href="/README-Alibaba Open API Integration Flowchart-1.eraserdiagram" data-element-id="a-k_kSQRKOeKbttWx1Tsn"><img src="/.eraser/LQCcXFqJOypzDrun3YnZ___3Jivg2tjMecMlrHwbIVIBR8f7U03___---diagram----6084e38ea7f655c95af1aa969aad35f4-Alibaba-Open-API-Integration-Flowchart.png" alt="" data-element-id="a-k_kSQRKOeKbttWx1Tsn" /></a>
<!-- end-eraser-additional-files -->
<!-- end-eraser-additional-content -->
<!--- Eraser file: https://app.eraser.io/workspace/LQCcXFqJOypzDrun3YnZ --->