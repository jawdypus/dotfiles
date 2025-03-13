# Config
This is my dotfiles.

## Dependencies:
- [Alacritty](https://alacritty.org/)
- [Swayfx](https://github.com/WillPower3309/swayfx)
- [Swaylock-effects](https://github.com/mortie/swaylock-effects) ([for fedora](https://copr.fedorainfracloud.org/coprs/vrumger/swaylock-effects/))
- [Waybar](https://github.com/Alexays/Waybar)
- [Wlogout](https://github.com/ArtsyMacaw/wlogout)
- [Rofi](https://github.com/davatorium/rofi)
- [Mako](https://github.com/emersion/mako)
- [Wlsunset](https://github.com/kennylevinsen/wlsunset)
- [Font Awesome](https://fontawesome.com/)
- [JetBrainsMonoNerd Font](https://www.nerdfonts.com/)

## Installation:
### Fedora:
Intall what is already in dnf:
```sh sudo dnf install alacritty waybar wlogout rofi fontawesome-fonts mako wlsunset```
Install swayfx and swaylock effects:
```sh
# Enable copr of swayfx
sudo dnf copr enable swayfx/swayfx
sudo dnf install swayfx

# Remove swaylock that comes with swayfx
sudo dnf remove swaylock

sudo dnf copr enable vrumger/swaylock-effects
sudo dn install swaylock-effects
```
