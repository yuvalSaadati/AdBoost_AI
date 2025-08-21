# 📈 AdBoost AI

AdBoost AI is an intelligent ad optimization tool powered by **Google Gemini AI** and a **CTR prediction model**.  
It helps marketers generate improved ad titles and descriptions, then predicts whether the new ad will have a higher Click-Through Rate (CTR).

---

## ✨ Features
- 🔮 AI-generated ad titles and descriptions (via Gemini API).
- 📊 CTR prediction using a trained machine learning model.
- 📂 Support for single ad input or bulk optimization via Excel file upload.
- 🌐 FastAPI backend with a simple web interface (form upload & JSON).
- 💾 Model persistence with `joblib`.

---

## ⚙️ Tech Stack
- **Backend**: [FastAPI](https://fastapi.tiangolo.com/)
- **AI**: [Google Gemini API](https://ai.google.dev/)
- **ML**: scikit-learn, joblib
- **Frontend**: HTML + JS form (fetch API)
- **Data**: Excel (`.xlsx`) file processing with `openpyxl`/`pandas`

---

## 📦 Installation

### 1. Clone Repository
```bash
git clone https://github.com/your-username/adboost-ai.git
cd adboost-ai
