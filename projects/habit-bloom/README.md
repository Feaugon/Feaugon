# Habit Bloom 2

Um jardim de pequenos passos: app desktop com painel do dia, visual claro em tons de verde, metas e conquistas. Python 3.10+ com Tkinter, sem bibliotecas externas.

## Novidades

- Painel com percentual de hábitos concluídos hoje e cartões de progresso.
- Categorias: Bem-estar, Saúde, Estudo, Trabalho e Pessoal.
- Metas de 1 a 7 dias por semana, de segunda-feira a domingo.
- Criar e editar hábitos, registrar uma motivação e buscar por nome ou categoria.
- Arquivar e restaurar sem perder o histórico.
- Histórico editável dos últimos 28 dias; datas futuras não são permitidas.
- Mapa de atividade, recorde de sequência e total de conclusões.
- 10 XP por conclusão, níveis a cada 100 XP e seis conquistas simbólicas.
- Exportação CSV para planilhas.

## Executar

```sh
python habit_bloom.py
```

Tkinter acompanha as distribuições oficiais usuais do Python para Windows e macOS. No Linux, pode ser necessário instalar `python3-tk` pelo gerenciador da distribuição.

Para escolher outro arquivo de dados:

```sh
python habit_bloom.py --data "meus-dados/habits.json"
```

## Dados da versão anterior

O app usa o mesmo arquivo `~/.habit-bloom/habits.json`. Ao abrir dados da versão 1, preserva nomes e registros e adiciona categoria Pessoal e meta de 7 dias. Antes do primeiro salvamento da versão 2, cria `habits.json.v1-backup.json` ao lado do original. Não abra as duas versões ao mesmo tempo e passe a usar apenas a versão 2 depois da migração.

Os dados ficam neste computador. Cada salvamento usa um arquivo temporário e substituição atômica. Arquivos inválidos são preservados, e o app mostra o erro ao abrir. Use uma instância por arquivo; não há sincronização entre instâncias.

## Regras do progresso

Cada hábito conta no máximo uma vez por data. Os pontos e conquistas são calculados a partir do histórico: desmarcar um registro remove os pontos correspondentes. Corrigir dias anteriores pode mudar níveis e conquistas. Arquivar mantém os pontos, sem criar novos. As recompensas não têm valor monetário.

A meta semanal é uma quantidade de dias, não um agendamento. A sequência diária e seu recorde continuam contando dias consecutivos, independentemente da meta. A semana atual inclui apenas registros de segunda-feira até hoje.

## Testes

```sh
python -m unittest discover -v
```

14 testes cobrem persistência, migração e backup, validação, datas, sequências, metas, XP, arquivamento, exportação e recuperação após falha ao salvar. A interface foi exercitada em testes de navegação, edição, histórico e arquivamento/restauração.

[← Voltar ao perfil](../../README.md)
