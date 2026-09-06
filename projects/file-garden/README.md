# File Garden

![File Garden](../../assets/file-garden.svg)

Um organizador por extensão que mostra o que vai fazer antes de alterar a pasta. **A execução padrão é somente uma prévia.**

## Rodar

Requer **Python 3.10+**, sem dependências externas. Na pasta deste projeto:

```sh
python file_garden.py "caminho/para/pasta"
```

Exemplo de prévia:

```text
FILE GARDEN / PRÉVIA — nenhum arquivo foi alterado

  foto.PNG  ->  Imagens/foto.PNG
  notas.txt  ->  Documentos/notas.txt

2 arquivo(s). Use --apply para executar.
```

Depois de conferir, execute:

```sh
python file_garden.py "caminho/para/pasta" --apply
```

O resultado é um relatório JSON no terminal. Código de saída `0` indica sucesso; `1` indica falha em pelo menos um movimento; argumentos inválidos retornam `2`.

## Comportamento

- Separa em Imagens, Documentos, Audio, Video, Compactados, Codigo e Outros.
- Examina apenas arquivos diretamente dentro da pasta; não percorre subpastas.
- Ignora nomes que começam com ponto e links simbólicos.
- Em colisões, escolhe `nome (1).ext`, `nome (2).ext` e assim por diante.
- Um destino que aparece após a prévia também é preservado; o movimento falha sem sobrescrevê-lo.
- Reexecutar depois de organizar não percorre os arquivos já movidos.

## Limites

Use em uma pasta local que não esteja sendo modificada por outro programa. Os movimentos usam links físicos seguidos da remoção da entrada original, exigindo um sistema de arquivos com suporte a hard links, como NTFS, APFS ou ext4. FAT/exFAT e alguns volumes de rede não são compatíveis: o original é mantido e o erro é informado.

Cada arquivo é processado individualmente; uma falha não desfaz os movimentos anteriores. Se a criação do link funcionar e a remoção da entrada original falhar, as duas entradas são preservadas e o relatório avisa. Esta versão não oferece desfazer automático.

## Testar

```sh
python -m unittest discover -v
```

Os testes usam apenas pastas temporárias e verificam prévia, colisões, conteúdo preservado, destino criado durante a operação e exclusão de arquivos ocultos/subpastas.

[← Voltar ao perfil](../../README.md)
