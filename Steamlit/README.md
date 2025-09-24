# Plantdrop

This project is a webinterface with Streamlit to display and edit data for Plants
## Project Structure

```
Streamlit
├── src
│   ├── .streamlit/
│   │    └── config.toml # configure the theme and other Streamlit options
│   └── styles
│   │    └── green_theme.css # Theme configurations for specific headers and stuff
│   ├── app.py # Main entry for Streamlit applications
├── Databases
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

To run the Streamlit application, execute the following command in your terminal:
```
python -m streamlit run src/app.py
```

This will start the Streamlit server and open the application in your default web browser.
