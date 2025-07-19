# Noesis Dashboard 🚀

## Visão Geral do Projeto

O **Noesis Dashboard** é uma aplicação desktop robusta e intuitiva, desenvolvida em Python com a poderosa biblioteca PyQt5. Meu objetivo é fornecer uma plataforma centralizada e elegante para estudantes possam gerenciarem e organizarem suas vidas acadêmicas e pessoais de forma eficiente.

Com uma interface moderna e personalizável, o Noesis Dashboard visa simplificar a organização de tarefas, acompanhamento de disciplinas, armazenamento de materiais e gestão de notas e eventos no calendário.

---

## Funcionalidades Principais ✨

- **Autenticação de Usuário:**  
  - Login seguro para usuários existentes com painel minimalista.  
  - Registro rápido e intuitivo para novos usuários.  
  - Modo Visitante para explorar o sistema sem criar conta.

- **Gerenciamento de Tarefas 📝:**  
  Criar, visualizar, editar, marcar como concluídas e excluir tarefas para manter seus prazos em dia.

- **Gerenciamento de Notas 💡:**  
  Adicionar e organizar notas rápidas, ideias e informações importantes.

- **Gerenciamento de Disciplinas 📚:**  
  Manter registros detalhados de disciplinas, horários, professores e mais.

- **Gerenciamento de Materiais 📁:**  
  Organizar documentos e recursos importantes por disciplina ou categoria.

- **Calendário 🗓️:**  
  Visualizar compromissos, prazos e eventos importantes em um calendário interativo.

- **Dashboard Personalizável 📊:**  
  Visão geral rápida das informações mais importantes com possibilidade de customização.

- **Temas 🎨:**  
  Alternar entre temas claro, escuro e ciano para adequar a aparência ao seu gosto.

---

## Tecnologias Utilizadas 🛠️

- Python  
- PyQt5  
- SQLite  
- QSS (Qt Style Sheets) para estilização  

---

## Requisitos do Sistema 💻
- Criar um ambiente é necessário para rodar.
- Python 3.6 ou superior  
- PyQt5 (`pip install PyQt5`)  
- SQLite3 (já incluído no Python)  

---
## Instalação 🚀

1. Clone o repositório:

   ```bash
   git clone https://github.com/fawkesenginner/noesis
   cd noesis

2. Crie e ative um ambiente virtual (Windows):

         python -m venv venv
        .\venv\Scripts\activate

 2. Criando ambiente no Mac/OS:
   
           python -m venv venv
          source venv/bin/activate
3. Instale as depêndencias

       pip install PyQt5

   
## Como Usar ▶️

Para iniciar a aplicação, com o ambiente virtual ativado, execute:

```bash
python login.py
 ```
Na tela de login:

- **Login:** Digite seu nome de usuário e senha, clique em **"ENTRAR"**.

- **Registro:** Caso não tenha conta, clique em **"Não é membro? Criar nova conta"**, preencha os dados e clique em **"REGISTRAR"**.

- **Modo Visitante:** Clique em **"ENTRAR COMO VISITANTE"** para acessar o dashboard com funcionalidades básicas.

- **Esqueceu a senha?:** Clique no link para informações (funcionalidade em desenvolvimento).

  ## Observações ✴

 - Ao criar o login.py ele automaticamente já gera uma database propria localhost.
 - A função de administrador você pode setar diratemente na database ou mudando no auth.py que é o autenticador.
 - O software está todo funcional principalmente o sistema crud, a inclusão de funcionalidades pode ser implementada, mas o software foi feito para estudo de interligação com o backend e pode ou não ter atualizações.
 - Faça um bom uso do software caso deseje testar ou implementar em algum projeto fique á vontade, no mais, agradeço.

 - Software desenvolvido para fins educacionais e de aprendizagem, Fawkes.


