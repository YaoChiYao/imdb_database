# IMDB Movie Database Project

A full-stack movie database web application that supports browsing, searching, user ratings and favorites, and AI-powered Q&A functionality.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React + Vite + React Router |
| Backend | Flask + Flask-CORS |
| Database | MySQL |
| AI | Anthropic Claude API |

## Project Structure

```
imdb_database/
├── backend/                    # Flask 后端
│   ├── app.py                  # Flask 应用入口，注册蓝图和 CORS
│   ├── config.py               # 数据库连接、AI API Key 等配置
│   ├── db.py                   # MySQL 数据库连接工具
│   ├── requirements.txt        # Python 依赖列表
│   ├── models/
│   │   ├── movie.py            # 电影相关数据库操作（查询、筛选、评分等）
│   │   └── user.py             # 用户相关数据库操作（注册、登录、收藏等）
│   ├── routes/
│   │   ├── movie_routes.py     # 电影 API 路由（/api/movies/*）
│   │   ├── user_routes.py      # 用户 API 路由（/api/users/*）
│   │   └── ai_routes.py        # AI 问答 API 路由（/api/ai/*）
│   └── utils/
│       ├── auth.py             # JWT Token 生成与验证工具
│       └── ai_helper.py        # Claude AI 接口封装
│
├── frontend/                   # React 前端
│   ├── package.json            # Node.js 依赖和脚本
│   ├── vite.config.js          # Vite 构建配置（含 API 代理）
│   ├── index.html              # HTML 入口
│   └── src/
│       ├── main.jsx            # React 应用挂载入口
│       ├── App.jsx             # 根组件，定义路由结构
│       ├── api/
│       │   ├── movieApi.js     # 封装电影相关 HTTP 请求
│       │   └── userApi.js      # 封装用户相关 HTTP 请求
│       ├── context/
│       │   └── AuthContext.jsx # 全局用户认证状态管理（Context + localStorage）
│       ├── components/
│       │   ├── Navbar.jsx      # 顶部导航栏（含登录状态显示）
│       │   ├── MovieCard.jsx   # 电影卡片组件（封面、标题、评分）
│       │   └── SearchBar.jsx   # 搜索框组件
│       └── pages/
│           ├── MovieList.jsx   # 电影列表页（搜索、筛选、分页）
│           ├── MovieDetail.jsx # 电影详情页（评论、评分、收藏）
│           ├── AIPage.jsx      # AI 智能问答页面
│           ├── Login.jsx       # 登录页面
│           ├── Register.jsx    # 注册页面
│           └── Profile.jsx     # 个人主页（收藏、评分历史）
│
├── apidoc/                     # API 文档（apidoc 生成的静态页面）
│   └── index.html              # API 文档入口
│
└── .gitignore                  # Git 忽略配置
```

---


## Main Features

- **Movie Browsing**: Paginated movie list with filtering by title, genre, and year, plus search functionality  
- **Movie Details**: View detailed information, user reviews, and ratings  
- **User System**: Register, login (JWT authentication), and profile page  
- **Favorites and Ratings**: Logged-in users can favorite movies, submit ratings, and leave reviews  
- **AI Q&A**: Integrated Claude API for natural language queries about movies  

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```
---

## Environment Configuration

In backend/config.py, set the following:

```python
DB_HOST = "localhost"
DB_USER = "your_db_user"
DB_PASSWORD = "your_db_password"
DB_NAME = "imdb_database"
JWT_SECRET = "your_jwt_secret"
CLAUDE_API_KEY = "your_anthropic_api_key"
```

---

## API Documentation

Full API documentation is available at ./backend/API_DOC.md