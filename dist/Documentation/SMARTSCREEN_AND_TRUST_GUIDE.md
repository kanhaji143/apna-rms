# Microsoft Defender SmartScreen & Publisher Guide
### APNA Computer Record Management System (RMS) v2.0

---

## 1. स्मार्टस्क्रीन (SmartScreen) क्या है और क्यों आता है?
जब भी कोई सॉफ़्टवेयर पहली बार किसी कंप्यूटर पर नेटवर्क शेयर (LAN) या इंटरनेट से कॉपी होकर आता है, तो Windows 10/11 उस पर एक सुरक्षा टैग लगा देता है (**Mark of the Web**)। 
क्योंकि यह सॉफ़्टवेयर नया है और अभी दुनिया भर के लाखों कंप्यूटरों पर डाउनलोड नहीं हुआ है, इसलिए माइक्रोसॉफ्ट डिफ़ेंडर एक सुरक्षा सूचना (Blue Banner) दिखाता है:
> *"Windows protected your PC. Microsoft Defender SmartScreen prevented an unrecognized app from starting."*

**यह कोई वायरस नहीं है, बल्कि विंडोज़ की एक सामान्य चेतावनी है।**

---

## 2. 'Unknown Publisher' कैसे ठीक हुआ?
हमने सॉफ़्टवेयर में **आधिकारिक डिजिटल हस्ताक्षर (Authenticode Digital Signature)** जोड़ दिया है:
- **हस्ताक्षरकर्ता (Signer):** `APNA Computer Institute`
- **संगठन (Organization):** `APNA Computer`
- जब आप फ़ाइल पर `Right-Click -> Properties -> Digital Signatures` देखेंगे, तो वहां `APNA Computer Institute` का डिजिटल हस्ताक्षर दिखाई देगा।

---

## 3. स्मार्टस्क्रीन को 5 सेकंड में हटाने के 2 आसान तरीके:

### तरीका 1: 'Unblock' चेकबॉक्स (सबसे तेज़ - 5 सेकंड)
1. जब आप दूसरे पीसी में `APNA_Computer_RMS_Setup.exe` कॉपी करें, तो उस फ़ाइल पर **राइट-क्लिक (Right Click)** करें।
2. **Properties (प्रॉपर्टीज़)** पर क्लिक करें।
3. सबसे नीचे 'Security' के सामने **☑️ Unblock (अनब्लॉक)** वाले बॉक्स पर टिक करें।
4. **Apply** दबाएं और फिर **OK** दबाएं।
5. अब जब आप डबल-क्लिक करेंगे, तो कोई स्मार्टस्क्रीन पॉप-अप नहीं आएगा और ऐप सीधे खुल जाएगा!

### तरीका 2: 'More info' -> 'Run anyway' (सामान्य तरीका)
1. जब नीला बॉक्स आए, तो **"More info"** पर क्लिक करें।
2. अब नीचे दिखने वाले **"Run anyway"** बटन पर क्लिक करें।
3. एक बार चलने के बाद विंडोज़ इसे सुरक्षित मान लेता है और उस पीसी पर यह चेतावनी दोबारा कभी नहीं आती।

### तरीका 3: 1-क्लिक ट्रस्ट इंस्टॉलर (स्थायी पहचान)
1. फ़ोल्डर में दी गई `Trust_APNA_Certificate.bat` फ़ाइल पर डबल-क्लिक करें।
2. यह आपके कंप्यूटर में `APNA Computer Institute` के सर्टिफ़िकेट को 'विश्वसनीय पब्लिशर' (Trusted Publisher) के रूप में रजिस्टर कर देगा।
