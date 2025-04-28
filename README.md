### Everything runs with:

#### Backend
```bash
cd backend && python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
```
python app.py

#### Frontend
```bash
cd ../frontend
npm install
npm run dev
```

### Proyect Map
```text
fitgirlsite-webscraping/
├── backend/
│   ├── app.py
│   ├── scraper.py
│   └── requirements.txt
└── frontend/
    ├── package.json   # Next 13 + Tailwind v4
    ├── tailwind.config.js
    ├── postcss.config.js
    └── app/
        └── page.tsx   # simple UI
```