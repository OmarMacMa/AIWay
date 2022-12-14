# AIWay

AI Way is a HackMTY 2022 project that uses crowdfunding to improve and grow the product. Our community can contribute by using our WhatsApp bot, which was programmed with the Twilio API, to report security incidents and traffic accidents. The bot uses natural language processing (NLP) powered by DeepL and OpenAI APIs to categorize the reports and stores them in a PostgreSQL database.

We then use this data to create a realtime map, powered by the Google Maps API, that shows traffic incidents in yellow and security incidents in red. The map works as a heatmap, with more intense colors indicating a higher concentration of reports in a given area. This helps the community avoid dangerous areas and allows authorities to improve the security of their cities. The map can display reports from anywhere in the world, including Mexico and Japan.

The web page was built using the Django web framework and Python 3.8.