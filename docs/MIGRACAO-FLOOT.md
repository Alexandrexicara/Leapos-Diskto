# Migracao do prototipo Floot para o desktop Linux

A interface web do Floot era uma demonstracao interativa. As funcoes foram reimplementadas como aplicativos locais Python/PyQt6 neste repositorio; nao se carrega o site Floot dentro do desktop.

## Funcionalidades migradas nesta etapa
- Desktop LeapOS em PyQt6 com menu Iniciar, atalhos e relogio.
- Arquivos locais, criacao de pasta e envio de arquivos para a lixeira via GVFS.
- Navegador com Qt WebEngine (fallback para navegador do sistema).
- Bloco de notas, calculadora com parser restrito, fotos, videos e musica.
- Assistente NVIDIA NIM e voz ElevenLabs usando .env local.
- Catalogo local de aplicativos integrados. O registro ativo confirmado na base do Floot nesta migracao e TelePronto.

## Limites
- O catalogo e uma copia inicial dos registros ativos consultados na base Floot; sincronizacao dinamica e autenticacao/licencas precisam de API segura do portal.
- O site TelePronto pode impedir incorporacao por iframe; o catalogo abre em janela WebEngine e pode usar navegador externo.
- O sistema ainda precisa ser compilado, testado em VM e refinado. Nao e instalador de disco pronto.
