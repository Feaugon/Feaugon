# Laboratório Feaugon

Três aplicativos independentes em Python 3.10+, construídos como projetos de estudo. Cada pasta inclui código executável, instruções de uso e testes.

| Projeto | Interface | Iniciar na pasta do projeto |
| --- | --- | --- |
| [Focus Flow](focus-flow) | Desktop / Tkinter | `python focus_flow.py` |
| [File Garden](file-garden) | Terminal | `python file_garden.py "pasta"` |
| [Habit Bloom 2](habit-bloom) | Desktop / Tkinter | `python habit_bloom.py` |

## Baixar e experimentar

```sh
git clone https://github.com/Feaugon/Feaugon.git
cd Feaugon
python run_tests.py
```

Você também pode usar **Code → Download ZIP** no repositório e extrair os arquivos.

## Validação desta versão

- **24 testes automatizados aprovados** em Python 3.12 no Windows: 5 do timer, 5 do organizador e 14 dos hábitos.
- O organizador foi exercitado com arquivos temporários; nenhum arquivo pessoal foi usado.
- A inicialização das interfaces foi validada. No Habit Bloom 2, os testes de interface também exercitam navegação, edição, histórico e arquivamento/restauração.
- A revisão visual dos banners SVG foi concluída. Eles são ilustrações de apresentação, não capturas de tela dos aplicativos.

[← Voltar ao perfil](../README.md)
