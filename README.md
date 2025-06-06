# Car API

## Membros do Grupo
1. Leonardo Pessoa Miranda
2. Pedro Gomes Santiago Pires Beltrão
3. Vitor Hugo Coelho Cruz

## Explicação do Sistema
Este é um sistema CRUD (Create, Read, Update, Delete) para gerenciamento de carros, desenvolvido com FastAPI. O sistema permite:
- Adicionar novos carros com marca, modelo, ano, cor e preço
- Adicionar novos proprietários
- Listar todos os carros e proprietários cadastrados
- Buscar um carro e um proprietários específico por ID
- Atualizar informações de um carro e proprietários existentes
- Remover carros e proprietários do sistema
- Relacionar carros e proprietários

O banco de dados é em memória, o que significa que os dados são perdidos quando o servidor é reiniciado.

## Tecnologias Utilizadas
- **FastAPI**: Framework web moderno para construção de APIs com Python
- **Pydantic**: Para validação de dados e modelos
- **Pytest**: Para testes unitários
- **Pytest-cov**: Para medição de cobertura de testes
- **GitHub Actions**: Para integração contínua
- **Codecov**: Para visualização de relatórios de cobertura

## Como Executar
1. Instale as dependências: `pip install -r requirements.txt`
2. Execute o servidor: `uvicorn app.main:app --reload`
3. Acesse a documentação em: http://localhost:8000/docs