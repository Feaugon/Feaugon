# Laboratório Feaugon

Três aplicativos independentes em Python 3.10+, construídos como projetos de estudo. Cada pasta inclui código executável, instruções de uso e testes.

| Projeto | Interface | Iniciar na pasta do projeto |
| --- | --- | --- |
| [Focus Flow](focus-flow) | Desktop / Tkinter | `python focus_flow.py` |
| [File Garden](file-garden) | Terminal | `python file_garden.py "pasta"` |
| [Habit Bloom](habit-bloom) | Desktop / Tkinter | `python habit_bloom.py` |

## Baixar e experimentar

```sh
git clone https://github.com/Feaugon/Feaugon.git
cd Feaugon
python run_tests.py
```

Você também pode usar **Code → Download ZIP** no repositório e extrair os arquivos.

## Validação desta versão

- **16 testes automatizados aprovados** em Python 3.11 no Windows: 5 do timer, 5 do organizador e 6 dos hábitos.
- O organizador foi exercitado com arquivos temporários; nenhum arquivo pessoal foi usado.
- A construção das janelas não pôde ser validada no ambiente de desenvolvimento por falha na inicialização do Tcl/Tk. Os testes do timer e da persistência não dependem de abrir janelas.
- A revisão visual dos banners SVG foi concluída. Eles são ilustrações de apresentação, não capturas de tela dos aplicativos.

[← Voltar ao perfil](../README.md)
