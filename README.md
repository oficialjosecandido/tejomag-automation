# TejoMag - Informação além das margens

TejoMag é uma aplicação web que coleta notícias de fontes internacionais (BBC e Le Monde) e as traduz para português, permitindo que os leitores portugueses tenham acesso a informações globais em sua língua nativa.

## 🌍 Características

- **Notícias Internacionais**: Coleta automática de notícias da BBC e Le Monde
- **URLs Amigáveis**: Slugs baseados nos títulos dos artigos para melhor SEO
- **Tradução Completa**: Tradução inteligente do texto completo para português
- **Galeria de Imagens**: Extração e exibição de todas as imagens dos artigos originais
- **Categorização Inteligente**: Classificação automática em categorias relevantes
- **Interface Moderna**: Design limpo e responsivo com TejoMag branding
- **Atualização Automática**: Sistema de agendamento que busca novas notícias a cada hora

## 🚀 Tecnologias Utilizadas

### Backend
- **Python 3.x** - Linguagem principal
- **Flask** - Framework web
- **SQLite** - Base de dados
- **BeautifulSoup** - Web scraping
- **DeepL** - Tradução automática de alta qualidade
- **Requests** - HTTP client
- **Schedule** - Agendamento automático

### Frontend
- **React.js** - Framework frontend
- **React Router** - Navegação
- **Axios** - HTTP client
- **Inline Styles** - Styling (sem dependências CSS complexas)

## 📂 Estrutura do Projeto

```
tejomag-automation/
├── backend/
│   ├── app.py              # API Flask com scraping e agendamento
│   ├── scheduler.py        # Agendador standalone (opcional)
│   ├── news.db            # Base de dados SQLite (gerada automaticamente)
│   └── (venv/)            # Ambiente virtual Python
├── frontend/
│   ├── public/            # Arquivos públicos
│   ├── src/
│   │   ├── App.js         # Componente e rotas principais
│   │   ├── components/    # Componentes reutilizáveis
│   │   └── pages/         # Páginas da aplicação
│   └── package.json       # Dependências Node.js
├── requirements.txt       # Dependências Python
├── setup.sh              # Script de instalação rápida
├── LICENSE               # Licença MIT
└── README.md            # Este arquivo
```

## 🛠️ Instalação e Configuração

### Pré-requisitos
- Python 3.7+
- Node.js 14+
- npm

### Instalação Rápida

1. **Obtenha chave API do DeepL (grátis):**
   ```bash
   # Visite: https://www.deepl.com/pro-api
   # Conta gratuita: 500,000 caracteres/mês
   export DEEPL_API_KEY="sua-chave-aqui"
   ```

2. **Execute o script de instalação:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

O script irá:
- Instalar dependências Python (incluindo DeepL)
- Instalar dependências Node.js
- Iniciar backend em `http://localhost:5002`
- Iniciar frontend em `http://localhost:3001`

### Instalação Manual

#### Backend
```bash
cd backend
pip install -r ../requirements.txt
python app.py
```

A API estará disponível em `http://localhost:5002`

#### Frontend (React)

1. Instale as dependências:
```bash
cd frontend
npm install
```

2. Execute a aplicação:
```bash
npm start
```

A aplicação estará disponível em `http://localhost:3001`

## 📡 Endpoints da API

- `GET /api/health` - Verificação de saúde da API
- `GET /api/news` - Obter todas as notícias (com slugs e imagens)
- `GET /api/news/slug/<slug>` - Obter artigo específico por slug
- `GET /api/news/search?q=query` - Pesquisar notícias por título ou conteúdo
- `GET /api/news/categories` - Obter categorias disponíveis
- `GET /api/news/category/<category>` - Obter notícias por categoria
- `POST /api/news/refresh` - Atualizar notícias manualmente
- `GET /api/scheduler/status` - Verificar status do agendador

### Exemplo de Resposta de Artigo
```json
{
  "id": 1,
  "title": "Original English Title",
  "title_pt": "Título Traduzido em Português",
  "content": "Full original content...",
  "content_pt": "Conteúdo completo traduzido...",
  "image_url": "https://example.com/main-image.jpg",
  "images": ["image1.jpg", "image2.jpg", "image3.jpg"],
  "slug": "titulo-traduzido-em-portugues",
  "url": "https://bbc.com/news/article",
  "source": "BBC",
  "category": "Tecnologia",
  "scraped_at": "2025-10-06T22:38:00"
}
```

## ⏰ Sistema de Agendamento Automático

TejoMag inclui um sistema automático integrado que busca notícias a cada hora:

### Funcionalidades:
- **Busca Automática**: Coleta as 3 notícias mais recentes da BBC e Le Monde
- **Tradução Completa**: Traduz automaticamente até 20 parágrafos para português com DeepL
- **Geração de Slugs**: Cria URLs amigáveis em português automaticamente
- **Extração de Imagens**: Captura imagens relevantes dos artigos
- **Categorização Inteligente**: Classifica automaticamente em 11 categorias
- **Prevenção de Duplicatas**: Evita salvar notícias já existentes
- **Logs Detalhados**: Mostra o progresso de cada execução

### Como Funciona

**O agendador roda automaticamente em background:**
- ⏰ Busca notícias a cada hora
- 🔄 Roda independentemente do servidor
- 📊 Não bloqueia o startup

**Primeira vez?** As notícias aparecerão na próxima hora completa (ex: 00:00, 01:00, 02:00, etc.)

**Quer notícias imediatamente?** Use o endpoint:
```bash
curl -X POST http://localhost:5002/api/news/refresh
```

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

## 🔧 Funcionalidades Técnicas

### URLs com Slugs
Os artigos usam slugs amigáveis baseados nos títulos:
- Antes: `/article/4`
- Agora: `/article/trump-announces-new-trade-deal-with-china`

### Extração de Imagens
O sistema extrai todas as imagens relevantes dos artigos:
- Filtra logos, ícones e placeholders automaticamente
- Armazena múltiplas imagens por artigo
- Exibe galeria de imagens no artigo completo

### Tradução Completa
- Extrai até 20 parágrafos (vs. 8 anteriormente)
- Divide textos longos em chunks para melhor qualidade
- Detecta idioma automaticamente (EN/FR)

### Categorização Inteligente
Analisa título e conteúdo para classificar em:
Política, Economia, Tecnologia, Saúde, Desporto, Cultura, Guerra e Conflitos, Ambiente, Direitos Humanos, Ciência, Geral

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