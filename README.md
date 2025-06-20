# SunPower Maxeon Integration for Home Assistant

**⚠️ Important: API Access Requirements**

To use this integration, you **must first obtain API access credentials** from SunPower Maxeon. Please carefully follow the instructions in the official API documentation: [https://api.sunpowerglobal.com/docs/](https://api.sunpowerglobal.com/docs/)

- Contact Maxeon at 📧 **api@maxeon.com** to request access.
- If your application is approved, you’ll be asked to sign the API Terms of Use Agreement.
- Once signed, you will receive your **Client ID** and **Client Secret**.

> 🔑 **Pre-requisites**  
> You *must* have a **Client ID** and **Client Secret** to use this integration. These are only provided after registration and approval by Maxeon.

### 🔄 Redirect URI

When registering your application with Customer Service, use the following **recommended** redirect URI:

```
https://my.home-assistant.io/redirect/oauth
```

Alternatively, you may use a custom redirect URI like:

```
https://your-domain:PORT/auth/external/callback
```

However, this second option requires:
- **HTTPS** enabled for your Home Assistant instance.
- Disabling the default `my.home-assistant.io` redirect by using the [default_config_disabler](https://github.com/tronikos/default_config_disabler) custom integration.

---

## SunPower Maxeon Integration for Home Assistant

This is a custom integration for Home Assistant that allows you to monitor your SunPower Maxeon solar system.

⚠️ This project is not affiliated with or endorsed by SunPower or Maxeon.

### Features

- OAuth2 authentication with automatic token refresh and reAuth 
- Sensor platform for system status, metadata and monitoring  
- Configurations for controls systems  

---

## Installation

### Manual Installation

1. Clone or download this repository.
2. Copy the `sunpower_maxeon/` folder into your Home Assistant `custom_components/` directory.
3. Restart Home Assistant.
4. Go to **Settings → Devices & Services → Add Integration** and search for **"SunPower Maxeon"**.

### HACS (Home Assistant Community Store)

Optional but recommended for easier updates.

1. Go to **HACS → Integrations → Custom repositories**.
2. Add this repo:

    ```
    URL: https://github.com/geims12/sunpower_maxeon  
    Category: Integration
    ```

3. Install it, then restart Home Assistant.
4. Add the integration through the UI.

---

## Requirements

- Home Assistant 2025.4.4 or newer  
- A SunPower Maxeon account with API access  

---

## Configuration

This integration uses Home Assistant’s OAuth2 config flow. When you set it up, you’ll be redirected to log in with your SunPower Maxeon credentials.

No YAML configuration is necessary.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.
