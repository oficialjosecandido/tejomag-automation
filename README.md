# TejoMag - Informação além das margens

TejoMag é uma aplicação web que coleta notícias de fontes internacionais (BBC, Le Monde, A Marca, etc.) e as traduz para português, permitindo que os leitores portugueses tenham acesso a informações globais em sua língua nativa.

## 🌍 Características

- **Notícias Internacionais**: Coleta automática de notícias das principais fontes europeias
- **Tradução Automática**: Tradução inteligente para português usando Google Translate
- **Categorização Inteligente**: Classificação automática em categorias relevantes
- **Interface Moderna**: Design limpo e responsivo com TejoMag branding
- **SEO Otimizado**: Meta tags e estrutura otimizada para motores de busca

## 🚀 Tecnologias Utilizadas

### Backend
- **Python 3.x** - Linguagem principal
- **Flask** - Framework web
- **SQLite** - Base de dados
- **BeautifulSoup** - Web scraping
- **Google Translate** - Tradução automática
- **Requests** - HTTP client

### Frontend
- **React.js** - Framework frontend
- **React Router** - Navegação
- **Axios** - HTTP client
- **Inline Styles** - Styling (sem dependências CSS complexas)

## 📂 Estrutura do Projeto

```
tejomag-automation/
├── backend/
│   ├── app.py              # Aplicação Flask principal
│   ├── requirements.txt    # Dependências Python
│   └── news.db            # Base de dados SQLite (gerada automaticamente)
├── frontend/
│   ├── public/
│   │   ├── index.html     # HTML principal
│   │   └── manifest.json  # Manifest PWA
│   ├── src/
│   │   ├── App.js         # Componente principal
│   │   ├── components/
│   │   │   └── Layout.js  # Layout da aplicação
│   │   └── pages/
│   │       ├── HomePage.js      # Página inicial
│   │       └── ArticleDetailPage.js # Página de detalhes
│   ├── package.json       # Dependências Node.js
│   └── package-lock.json  # Lock file (gerado automaticamente)
├── .gitignore            # Arquivos a ignorar no Git
└── README.md            # Este arquivo
```

## 🛠️ Instalação e Configuração

### Pré-requisitos
- Python 3.7+
- Node.js 14+
- npm ou yarn

### Backend (API)

1. Navegue para a pasta backend:
```bash
cd backend
```

2. Crie um ambiente virtual (recomendado):
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute a aplicação:
```bash
python app.py
```

A API estará disponível em `http://localhost:5001`

### Frontend (React)

1. Navegue para a pasta frontend:
```bash
cd frontend
```

2. Instale as dependências:
```bash
npm install
```

3. Execute a aplicação:
```bash
npm start
```

A aplicação estará disponível em `http://localhost:3001`

## 📡 Endpoints da API

- `GET /api/health` - Verificação de saúde da API
- `GET /api/news` - Obter todas as notícias
- `GET /api/news/categories` - Obter categorias disponíveis
- `GET /api/news/category/<category>` - Obter notícias por categoria

## 🏷️ Categorias Disponíveis

- **Política** - Política, eleições, governo
- **Economia** - Economia, mercados, finanças
- **Tecnologia** - Tecnologia, ciência, inovação
- **Saúde** - Saúde, medicina, cuidados de saúde
- **Desporto** - Desporto, atletismo, competições
- **Cultura** - Cultura, artes, entretenimento
- **Guerra e Conflitos** - Guerra, conflitos, militar
- **Ambiente** - Clima, ambiente, sustentabilidade
- **Direitos Humanos** - Direitos humanos, justiça, lei
- **Ciência** - Ciência, investigação, descobertas
- **Geral** - Notícias gerais

## 🎨 Design e Branding

TejoMag utiliza uma paleta de cores consistente:
- **Cor Principal**: #1f6cac (Azul TejoMag)
- **Categorias**: Cada categoria tem sua própria cor distintiva
- **Tipografia**: Arial, sans-serif para consistência
- **Layout**: Design responsivo e moderno

## 🔧 Desenvolvimento

### Adicionar Nova Fonte de Notícias

1. Crie uma nova função de scraping em `backend/app.py`
2. Adicione a fonte à lista de fontes em `scrape_news()`
3. Teste a integração

### Modificar Categorias

1. Edite o dicionário `categories` em `detect_category()`
2. Atualize a lista em `get_categories()` endpoint
3. Ajuste as cores no frontend se necessário

### Personalizar Tradução

1. Modifique a função `translate_to_portuguese()`
2. Ajuste parâmetros de qualidade e velocidade
3. Teste com diferentes tipos de conteúdo

## 📄 Licença

Este projeto é de código aberto e está disponível sob a licença MIT.

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor:

1. Faça fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📞 Suporte

Para questões ou suporte, abra uma issue no repositório GitHub.

---

**TejoMag** - Conectando o mundo através das notícias em português 🌍📰