# TiMan

TiMan ist ein Web-Interface für unsere TI-GW-SECUNET-Kunden.

Kurz gesagt hilft TiMan dabei, Installationen schneller durchzuführen und Probleme einfacher zu analysieren bzw. zu dokumentieren.

Technisch gesehen ist TiMan eine Binary, die als Service dauerhaft auf Alpaquita Linux läuft.

---

# Verwendung mit unserem Image

Auf dem Alpaquita-Linux-System zunächst die IP-Adresse der Maschine herausfinden:

```bash
ip addr
```

Danach im Browser öffnen:

```text
http://<IP>:5000
```

## Zugangsdaten

```text
Benutzername: vm
Passwort: vm
```

---

# Verwendung auf einer Raw-Maschine

## Voraussetzungen installieren

```bash
sudo apk add curl
```

## Binary herunterladen

```bash
curl -L https://vm-tiaas.visionmaxx.net/ti-gw/timan/timan.bin -o timan.bin
```

## Ausführbar machen

```bash
sudo chmod +x timan.bin
```

## TiMan starten

```bash
sudo ./timan.bin
```
