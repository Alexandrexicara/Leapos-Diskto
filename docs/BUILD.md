# Construir a ISO Live

A imagem inicial usa Debian Trixie amd64, XFCE e teclado/localizacao brasileiros.

## GitHub Actions
Abra a aba Actions do repositorio e execute **Construir ISO LeapOS** em Run workflow. Ao concluir, baixe o artefato `leapos-live-iso`.

## Build local
Em uma maquina Debian/Ubuntu amd64 com internet e pelo menos 25 GB livres, instale live-build, debootstrap, xorriso, squashfs-tools, grub-pc-bin, grub-efi-amd64-bin, mtools e dosfstools. Na raiz do projeto execute:

```sh
sudo sh auto/config
sudo lb build
```

A ISO gerada e uma sessao Live para testes em maquina virtual ou pendrive. Ela nao possui instalador proprio e nao deve ser usada para instalar no disco interno.
