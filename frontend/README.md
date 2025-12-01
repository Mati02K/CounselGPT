# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.


## CounselGPT Frontend

## 🚀 Quick Start

### Local Development

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create `.env` file (copy from `env.example`):
   ```bash
   cp env.example .env
   ```

3. Start dev server:
   ```bash
   npm run dev
   ```

4. Open browser at `http://localhost:5173`

## ⚙️ Configuration

### Environment Variables

Edit the `.env` file to configure your backend:

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API endpoint | (set in deployment) |
| `VITE_MODELS` | Available models (JSON array) | See `.env` file |
| `VITE_DEFAULT_MODEL` | Default selected model | `qwen2.5-7b-legal` |

### Current Models

The frontend is configured with two models:

1. **Qwen2.5-7B Legal (LoRA)** - Fine-tuned legal model
2. **Qwen2.5-7B Base** - Base model

### Adding/Editing Models

Edit `VITE_MODELS` in `.env` file:

```env
VITE_MODELS=[
  {"id":"qwen2.5-7b-legal","name":"Qwen2.5-7B Legal (LoRA)"},
  {"id":"qwen2.5-7b-base","name":"Qwen2.5-7B Base"},
  {"id":"your-custom-model","name":"Your Custom Model"}
]
```

After editing `.env`, restart the dev server (Ctrl+C, then `npm run dev`)

## 📦 Deployment

### GitHub Pages (Recommended)

This project is configured for automatic deployment to GitHub Pages using GitHub Actions.

**Quick Setup:**
1. Enable GitHub Pages in your repo: Settings → Pages → Source: GitHub Actions
2. Push to `main` branch
3. Your site will be live at `https://YOUR_USERNAME.github.io/CounselGPT/`

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

### Manual Build

```bash
npm run build
```

The built files will be in the `dist` folder.
