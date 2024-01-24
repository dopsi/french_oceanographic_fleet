# Logos

The logos are taken from the website of the French oceanographic fleet.

They were converted for [home-assistant/brands](https://github.com/home-assistant/brands) (see [#5131](https://github.com/home-assistant/brands/pull/5131)) with:

```
convert -density 3000 -background none french_oceanographic_fleet_logo.svg  -resize "x256"  logo.png
```