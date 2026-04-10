#!/usr/bin/env python3
"""Seed the campers database with realistic test data."""

import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "campers.db"

CAMPERS = [
    {
        "marktplaats_id": "m2012345678",
        "title": "Hymer B-Class ModernComfort 580 - 2020 - Automaat",
        "price": 6995000,
        "location": "Amsterdam",
        "url": "https://www.marktplaats.nl/v/campers-caravans/campers-bussen/m2012345678-hymer-b-class-moderncomfort-580",
        "raw_html": "Prachtige Hymer B-Class ModernComfort 580 uit 2020. Automaat, Mercedes Sprinter chassis. Volledig uitgerust met airco, navigatie, achteruitrijcamera en zonnepanelen. 2 vaste slaapplaatsen achter + dinette omklap. Alles in topstaat, altijd gestald. APK tot 06-2027.",
        "image_urls": ["https://images.unsplash.com/photo-1561361513-2d000a50f0dc?w=800", "https://images.unsplash.com/photo-1543857778-c4a1a3e0b2eb?w=800", "https://images.unsplash.com/photo-1596395463367-f3a2e4dabb06?w=800"],
        "parsed_data": {"basis": {"merk": "Hymer", "model": "B-Class ModernComfort 580", "bouwjaar": 2020, "kilometerstand": 42000, "kenteken": None}, "capaciteit": {"slaapplaatsen": 4, "zitplaatsen": 4, "vaste_bedden": 2, "opklap_bedden": 2}, "technisch": {"brandstof": "diesel", "transmissie": "automaat", "vermogen_PK": 163, "lengte_cm": 699}, "comfort": {"airco": True, "GPS": True, "parkeersensoren": True}, "camper": {"keuken": True, "koelkast": True, "douche": True, "toilet": True}, "onderhoud": {"APK_geldig": True, "service_historie": True}}
    },
    {
        "marktplaats_id": "m2023456789",
        "title": "Volkswagen California Ocean 6.1 - DSG - Slaaphefdak",
        "price": 7450000,
        "location": "Utrecht",
        "url": "https://www.marktplaats.nl/v/campers-caravans/campers-bussen/m2023456789-volkswagen-california-ocean",
        "raw_html": "VW California Ocean 6.1 met DSG automaat. Pop-up dak met 2 slaapplaatsen. Ingebouwde keuken, koelkast, standverwarming. Perfect voor weekend getaways. Dealer onderhouden.",
        "image_urls": ["https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=800", "https://images.unsplash.com/photo-1527786356703-4b100091cd2c?w=800"],
        "parsed_data": {"basis": {"merk": "Volkswagen", "model": "California Ocean 6.1", "bouwjaar": 2021, "kilometerstand": 35000, "kenteken": None}, "capaciteit": {"slaapplaatsen": 4, "zitplaatsen": 4, "vaste_bedden": 0, "opklap_bedden": 4}, "technisch": {"brandstof": "diesel", "transmissie": "automaat", "vermogen_PK": 150, "lengte_cm": 497}, "comfort": {"airco": True, "GPS": True, "parkeersensoren": True}, "camper": {"keuken": True, "koelkast": True, "douche": False, "toilet": False}, "onderhoud": {"APK_geldig": True, "service_historie": True}}
    },
    {
        "marktplaats_id": "m2034567890",
        "title": "Fiat Ducato Sunlight T68 - 2017 - Vast bed - Garage",
        "price": 4250000,
        "location": "Eindhoven",
        "url": "https://www.marktplaats.nl/v/campers-caravans/campers-bussen/m2034567890-fiat-ducato-sunlight-t68",
        "raw_html": "Ruime Sunlight T68 op Fiat Ducato basis. Vast queensbed achter, ruime garage eronder. 6 versnellingen handgeschakeld. Keuken met 3-pits, grote koelkast, douche en toilet. Ideaal voor langere reizen. APK tot 2026.",
        "image_urls": ["https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=800", "https://images.unsplash.com/photo-1530789253388-582c481c54b0?w=800", "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=800", "https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=800"],
        "parsed_data": {"basis": {"merk": "Fiat", "model": "Ducato Sunlight T68", "bouwjaar": 2017, "kilometerstand": 89000, "kenteken": None}, "capaciteit": {"slaapplaatsen": 4, "zitplaatsen": 4, "vaste_bedden": 2, "opklap_bedden": 2}, "technisch": {"brandstof": "diesel", "transmissie": "handgeschakeld", "vermogen_PK": 130, "lengte_cm": 699}, "comfort": {"airco": True, "GPS": False, "parkeersensoren": False}, "camper": {"keuken": True, "koelkast": True, "douche": True, "toilet": True}, "onderhoud": {"APK_geldig": True, "service_historie": True}}
    },
    {
        "marktplaats_id": "m2045678901",
        "title": "Mercedes Sprinter 316 CDI - Zelfbouw - Off-grid",
        "price": 3500000,
        "location": "Groningen",
        "url": "https://www.marktplaats.nl/v/campers-caravans/campers-bussen/m2045678901-mercedes-sprinter-316-zelfbouw",
        "raw_html": "Unieke zelfbouw camper op Mercedes Sprinter 316 CDI basis. Volledig off-grid met 400W zonnepanelen, 200Ah lithium accu. Houten interieur, vast bed, keuken met inductie. Geen douche maar buitendouche aanwezig.",
        "image_urls": ["https://images.unsplash.com/photo-1494783367193-149034c05e8f?w=800", "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=800"],
        "parsed_data": {"basis": {"merk": "Mercedes-Benz", "model": "Sprinter 316 CDI", "bouwjaar": 2016, "kilometerstand": 156000, "kenteken": None}, "capaciteit": {"slaapplaatsen": 2, "zitplaatsen": 2, "vaste_bedden": 2, "opklap_bedden": 0}, "technisch": {"brandstof": "diesel", "transmissie": "handgeschakeld", "vermogen_PK": 163, "lengte_cm": 700}, "comfort": {"airco": True, "GPS": False, "parkeersensoren": False}, "camper": {"keuken": True, "koelkast": True, "douche": False, "toilet": False}, "onderhoud": {"APK_geldig": True, "service_historie": False}}
    },
    {
        "marktplaats_id": "m2056789012",
        "title": "Knaus Van TI Plus 650 MEG - 2022 - Platinum Selection",
        "price": 8900000,
        "location": "Den Haag",
        "url": "https://www.marktplaats.nl/v/campers-caravans/campers-bussen/m2056789012-knaus-van-ti-plus-650",
        "raw_html": "Knaus Van TI Plus 650 MEG Platinum Selection. Topmodel met alle opties. Fiat Ducato 180 PK automaat. Enkele bedden achter, grote garage, volledig geïsoleerd, 4-seizoenen camper. Dealer onderhouden bij Knaus centrum.",
        "image_urls": ["https://images.unsplash.com/photo-1515876305430-f06edab8282a?w=800", "https://images.unsplash.com/photo-1508672019048-805c876b67e2?w=800", "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800"],
        "parsed_data": {"basis": {"merk": "Knaus", "model": "Van TI Plus 650 MEG", "bouwjaar": 2022, "kilometerstand": 18000, "kenteken": None}, "capaciteit": {"slaapplaatsen": 2, "zitplaatsen": 4, "vaste_bedden": 2, "opklap_bedden": 0}, "technisch": {"brandstof": "diesel", "transmissie": "automaat", "vermogen_PK": 180, "lengte_cm": 699}, "comfort": {"airco": True, "GPS": True, "parkeersensoren": True}, "camper": {"keuken": True, "koelkast": True, "douche": True, "toilet": True}, "onderhoud": {"APK_geldig": True, "service_historie": True}}
    },
    {
        "marktplaats_id": "m2067890123",
        "title": "Citroën Jumper - Pössl Roadcruiser - Compact",
        "price": 2850000,
        "location": "Breda",
        "url": "https://www.marktplaats.nl/v/campers-caravans/campers-bussen/m2067890123-citroen-jumper-possl-roadcruiser",
        "raw_html": "Compacte Pössl Roadcruiser op Citroën Jumper basis. Perfect voor stellen die een wendbare camper zoeken. Vast bed, kleine keuken, chemisch toilet. Handgeschakeld, zuinig in gebruik.",
        "image_urls": ["https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800"],
        "parsed_data": {"basis": {"merk": "Citroën", "model": "Jumper Pössl Roadcruiser", "bouwjaar": 2014, "kilometerstand": 112000, "kenteken": None}, "capaciteit": {"slaapplaatsen": 2, "zitplaatsen": 2, "vaste_bedden": 2, "opklap_bedden": 0}, "technisch": {"brandstof": "diesel", "transmissie": "handgeschakeld", "vermogen_PK": 130, "lengte_cm": 599}, "comfort": {"airco": True, "GPS": False, "parkeersensoren": False}, "camper": {"keuken": True, "koelkast": True, "douche": False, "toilet": True}, "onderhoud": {"APK_geldig": True, "service_historie": True}}
    },
    {
        "marktplaats_id": "m2078901234",
        "title": "Bürstner Lyseo TD 736 Harmony Line - Familiecamper",
        "price": 5650000,
        "location": "Nijmegen",
        "url": "https://www.marktplaats.nl/v/campers-caravans/campers-bussen/m2078901234-burstner-lyseo-td-736",
        "raw_html": "Ruime familiecamper Bürstner Lyseo TD 736 Harmony Line. 6 slaapplaatsen, waarvan 2 vast en 4 opklapbaar. Fiat Ducato 140 PK. Grote L-keuken, apart toilet en douche, veel bergruimte.",
        "image_urls": ["https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800", "https://images.unsplash.com/photo-1527004013197-933c4bb611b3?w=800", "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800"],
        "parsed_data": {"basis": {"merk": "Bürstner", "model": "Lyseo TD 736 Harmony Line", "bouwjaar": 2019, "kilometerstand": 62000, "kenteken": None}, "capaciteit": {"slaapplaatsen": 6, "zitplaatsen": 6, "vaste_bedden": 2, "opklap_bedden": 4}, "technisch": {"brandstof": "diesel", "transmissie": "handgeschakeld", "vermogen_PK": 140, "lengte_cm": 736}, "comfort": {"airco": True, "GPS": True, "parkeersensoren": True}, "camper": {"keuken": True, "koelkast": True, "douche": True, "toilet": True}, "onderhoud": {"APK_geldig": True, "service_historie": True}}
    },
    {
        "marktplaats_id": "m2089012345",
        "title": "Ford Transit Custom Nugget - 2023 - Nieuwstaat",
        "price": 6200000,
        "location": "Haarlem",
        "url": "https://www.marktplaats.nl/v/campers-caravans/campers-bussen/m2089012345-ford-transit-custom-nugget",
        "raw_html": "Ford Transit Custom Nugget in nieuwstaat. Nauwelijks gebruikt, 12.000 km. Slaaphefdak, keukenblok, koelkast, standverwarming. Automaat, adaptieve cruise control. Ideaal als dagelijks vervoer en weekendcamper.",
        "image_urls": ["https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=800", "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=800"],
        "parsed_data": {"basis": {"merk": "Ford", "model": "Transit Custom Nugget", "bouwjaar": 2023, "kilometerstand": 12000, "kenteken": None}, "capaciteit": {"slaapplaatsen": 4, "zitplaatsen": 5, "vaste_bedden": 0, "opklap_bedden": 4}, "technisch": {"brandstof": "diesel", "transmissie": "automaat", "vermogen_PK": 185, "lengte_cm": 497}, "comfort": {"airco": True, "GPS": True, "parkeersensoren": True}, "camper": {"keuken": True, "koelkast": True, "douche": False, "toilet": False}, "onderhoud": {"APK_geldig": True, "service_historie": True}}
    },
    {
        "marktplaats_id": "m2090123456",
        "title": "Adria Twin Supreme 640 SLB - 2019 - Lengtebedden",
        "price": 5100000,
        "location": "Tilburg",
        "url": "https://www.marktplaats.nl/v/campers-caravans/campers-bussen/m2090123456-adria-twin-supreme-640-slb",
        "raw_html": "Adria Twin Supreme 640 SLB met lengtebedden achter. Fiat Ducato 160 PK automaat. Volledig uitgerust: airco, navigatie, achteruitrijcamera, zonnepaneel 160W. Compacte buscamper met alles erop en eraan.",
        "image_urls": ["https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=800", "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800", "https://images.unsplash.com/photo-1519046904884-53103b34b206?w=800"],
        "parsed_data": {"basis": {"merk": "Adria", "model": "Twin Supreme 640 SLB", "bouwjaar": 2019, "kilometerstand": 54000, "kenteken": None}, "capaciteit": {"slaapplaatsen": 2, "zitplaatsen": 4, "vaste_bedden": 2, "opklap_bedden": 0}, "technisch": {"brandstof": "diesel", "transmissie": "automaat", "vermogen_PK": 160, "lengte_cm": 636}, "comfort": {"airco": True, "GPS": True, "parkeersensoren": True}, "camper": {"keuken": True, "koelkast": True, "douche": True, "toilet": True}, "onderhoud": {"APK_geldig": True, "service_historie": True}}
    },
    {
        "marktplaats_id": "m2101234567",
        "title": "Renault Master - Weinsberg CaraBus 601 MQH - 2016",
        "price": 3200000,
        "location": "Arnhem",
        "url": "https://www.marktplaats.nl/v/campers-caravans/campers-bussen/m2101234567-renault-master-weinsberg-carabus",
        "raw_html": "Weinsberg CaraBus 601 MQH op Renault Master. Alkoof met extra slaapplaats. Handgeschakeld, 145 PK. Keuken, koelkast, toilet. Geen douche. Geschikt voor 4 personen. APK verlopen, nieuwe APK bij verkoop.",
        "image_urls": ["https://images.unsplash.com/photo-1517760444937-f6397edcbbcd?w=800"],
        "parsed_data": {"basis": {"merk": "Renault", "model": "Master Weinsberg CaraBus 601", "bouwjaar": 2016, "kilometerstand": 134000, "kenteken": None}, "capaciteit": {"slaapplaatsen": 4, "zitplaatsen": 4, "vaste_bedden": 2, "opklap_bedden": 2}, "technisch": {"brandstof": "diesel", "transmissie": "handgeschakeld", "vermogen_PK": 145, "lengte_cm": 610}, "comfort": {"airco": False, "GPS": False, "parkeersensoren": False}, "camper": {"keuken": True, "koelkast": True, "douche": False, "toilet": True}, "onderhoud": {"APK_geldig": False, "service_historie": False}}
    },
    {
        "marktplaats_id": "m2112345678",
        "title": "Chausson Welcome 628 EB - 2018 - Enkele bedden",
        "price": 4800000,
        "location": "Zwolle",
        "url": "https://www.marktplaats.nl/v/campers-caravans/campers-bussen/m2112345678-chausson-welcome-628-eb",
        "raw_html": "Chausson Welcome 628 EB met enkele bedden achter. Fiat Ducato 130 PK. Ruim interieur, grote garage, apart toilet en douche. Airco cabine, cruise control. Dealer onderhouden.",
        "image_urls": ["https://images.unsplash.com/photo-1504609773096-104ff2c73ba4?w=800", "https://images.unsplash.com/photo-1501555088652-021faa106b9b?w=800"],
        "parsed_data": {"basis": {"merk": "Chausson", "model": "Welcome 628 EB", "bouwjaar": 2018, "kilometerstand": 71000, "kenteken": None}, "capaciteit": {"slaapplaatsen": 4, "zitplaatsen": 4, "vaste_bedden": 2, "opklap_bedden": 2}, "technisch": {"brandstof": "diesel", "transmissie": "handgeschakeld", "vermogen_PK": 130, "lengte_cm": 699}, "comfort": {"airco": True, "GPS": False, "parkeersensoren": False}, "camper": {"keuken": True, "koelkast": True, "douche": True, "toilet": True}, "onderhoud": {"APK_geldig": True, "service_historie": True}}
    },
    {
        "marktplaats_id": "m2123456789",
        "title": "Iveco Daily 35S18 - Laika Ecovip 612 - Luxe",
        "price": 7200000,
        "location": "Maastricht",
        "url": "https://www.marktplaats.nl/v/campers-caravans/campers-bussen/m2123456789-iveco-daily-laika-ecovip-612",
        "raw_html": "Luxe Laika Ecovip 612 op Iveco Daily 35S18 chassis. 180 PK automaat. Queen bed achter, grote L-keuken, apart toilet met douche. Volledig voorzien: airco, GPS, parkeersensoren, zonnepanelen, sat-TV. 4-seizoenen isolatie.",
        "image_urls": ["https://images.unsplash.com/photo-1534067783941-51c9c23ecefd?w=800", "https://images.unsplash.com/photo-1504457047772-27faf1c00561?w=800", "https://images.unsplash.com/photo-1503220317375-aaad61436b1b?w=800"],
        "parsed_data": {"basis": {"merk": "Iveco", "model": "Daily Laika Ecovip 612", "bouwjaar": 2021, "kilometerstand": 28000, "kenteken": None}, "capaciteit": {"slaapplaatsen": 4, "zitplaatsen": 4, "vaste_bedden": 2, "opklap_bedden": 2}, "technisch": {"brandstof": "diesel", "transmissie": "automaat", "vermogen_PK": 180, "lengte_cm": 699}, "comfort": {"airco": True, "GPS": True, "parkeersensoren": True}, "camper": {"keuken": True, "koelkast": True, "douche": True, "toilet": True}, "onderhoud": {"APK_geldig": True, "service_historie": True}}
    },
    {
        "marktplaats_id": "m2134567890",
        "title": "Peugeot Boxer - Hobby Vantana K65 ET - 2015",
        "price": 3100000,
        "location": "Leeuwarden",
        "url": "https://www.marktplaats.nl/v/campers-caravans/campers-bussen/m2134567890-peugeot-boxer-hobby-vantana",
        "raw_html": "Hobby Vantana K65 ET op Peugeot Boxer. Compact maar compleet. Vast bed, keuken, koelkast, chemisch toilet. Geen douche. Handgeschakeld 130 PK. Zuinig in verbruik. Nieuwe banden, APK vers.",
        "image_urls": ["https://images.unsplash.com/photo-1473496169904-658ba7c44d8a?w=800", "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=800"],
        "parsed_data": {"basis": {"merk": "Peugeot", "model": "Boxer Hobby Vantana K65", "bouwjaar": 2015, "kilometerstand": 98000, "kenteken": None}, "capaciteit": {"slaapplaatsen": 2, "zitplaatsen": 2, "vaste_bedden": 2, "opklap_bedden": 0}, "technisch": {"brandstof": "diesel", "transmissie": "handgeschakeld", "vermogen_PK": 130, "lengte_cm": 636}, "comfort": {"airco": True, "GPS": False, "parkeersensoren": False}, "camper": {"keuken": True, "koelkast": True, "douche": False, "toilet": True}, "onderhoud": {"APK_geldig": True, "service_historie": False}}
    },
    {
        "marktplaats_id": "m2145678901",
        "title": "Volkswagen Crafter - Grand California 600 - 2022",
        "price": 8500000,
        "location": "Rotterdam",
        "url": "https://www.marktplaats.nl/v/campers-caravans/campers-bussen/m2145678901-volkswagen-crafter-grand-california",
        "raw_html": "VW Grand California 600 op Crafter basis. Premium buscamper met alles. Vast bed beneden, hefdak met 2e slaapplaats. Keuken, koelkast, chemisch toilet, buitendouche. 177 PK automaat. Standverwarming, airco, groot touchscreen.",
        "image_urls": ["https://images.unsplash.com/photo-1539635278303-d4002c07eae3?w=800", "https://images.unsplash.com/photo-1551632811-561732d1e306?w=800", "https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=800"],
        "parsed_data": {"basis": {"merk": "Volkswagen", "model": "Grand California 600", "bouwjaar": 2022, "kilometerstand": 22000, "kenteken": None}, "capaciteit": {"slaapplaatsen": 4, "zitplaatsen": 4, "vaste_bedden": 2, "opklap_bedden": 2}, "technisch": {"brandstof": "diesel", "transmissie": "automaat", "vermogen_PK": 177, "lengte_cm": 600}, "comfort": {"airco": True, "GPS": True, "parkeersensoren": True}, "camper": {"keuken": True, "koelkast": True, "douche": True, "toilet": True}, "onderhoud": {"APK_geldig": True, "service_historie": True}}
    },
    {
        "marktplaats_id": "m2156789012",
        "title": "Fiat Ducato Challenger 260 - 2013 - Budget Camper",
        "price": 1950000,
        "location": "Apeldoorn",
        "url": "https://www.marktplaats.nl/v/campers-caravans/campers-bussen/m2156789012-fiat-ducato-challenger-260",
        "raw_html": "Budget camper voor instappers! Challenger 260 op Fiat Ducato. 115 PK, handgeschakeld. Basis keuken, koelkast, chemisch toilet. Geen douche. 210.000 km maar loopt als een zonnetje. APK verlopen.",
        "image_urls": ["https://images.unsplash.com/photo-1508739773434-c26b3d09e071?w=800"],
        "parsed_data": {"basis": {"merk": "Fiat", "model": "Ducato Challenger 260", "bouwjaar": 2013, "kilometerstand": 210000, "kenteken": None}, "capaciteit": {"slaapplaatsen": 4, "zitplaatsen": 4, "vaste_bedden": 2, "opklap_bedden": 2}, "technisch": {"brandstof": "diesel", "transmissie": "handgeschakeld", "vermogen_PK": 115, "lengte_cm": 650}, "comfort": {"airco": False, "GPS": False, "parkeersensoren": False}, "camper": {"keuken": True, "koelkast": True, "douche": False, "toilet": True}, "onderhoud": {"APK_geldig": False, "service_historie": False}}
    },
    {
        "marktplaats_id": "m2167890123",
        "title": "Dethleffs Globebus T1 - 2020 - Automaat - Compact",
        "price": 5500000,
        "location": "Den Bosch",
        "url": "https://www.marktplaats.nl/v/campers-caravans/campers-bussen/m2167890123-dethleffs-globebus-t1",
        "raw_html": "Compacte Dethleffs Globebus T1 met alles erop. Fiat Ducato 140 PK automaat. Vast dwarsbed, keuken, douche/toilet combo, airco. Perfect voor 2 personen. Laag verbruik, makkelijk te parkeren.",
        "image_urls": ["https://images.unsplash.com/photo-1506197603052-3cc9c3a201bd?w=800", "https://images.unsplash.com/photo-1501554728187-ce583db33af7?w=800"],
        "parsed_data": {"basis": {"merk": "Dethleffs", "model": "Globebus T1", "bouwjaar": 2020, "kilometerstand": 38000, "kenteken": None}, "capaciteit": {"slaapplaatsen": 2, "zitplaatsen": 4, "vaste_bedden": 2, "opklap_bedden": 0}, "technisch": {"brandstof": "diesel", "transmissie": "automaat", "vermogen_PK": 140, "lengte_cm": 599}, "comfort": {"airco": True, "GPS": True, "parkeersensoren": True}, "camper": {"keuken": True, "koelkast": True, "douche": True, "toilet": True}, "onderhoud": {"APK_geldig": True, "service_historie": True}}
    },
    {
        "marktplaats_id": "m2178901234",
        "title": "Toyota HiAce - Reimo Campervan - Oldtimer",
        "price": 1500000,
        "location": "Leiden",
        "url": "https://www.marktplaats.nl/v/campers-caravans/campers-bussen/m2178901234-toyota-hiace-reimo-campervan",
        "raw_html": "Klassieke Toyota HiAce met Reimo ombouw. Hefdak, simpele keuken, geen toilet/douche. Benzine motor, handgeschakeld. Charme van een oldtimer, compact genoeg voor de stad. Nieuwe APK.",
        "image_urls": ["https://images.unsplash.com/photo-1553697388-94e804e2f0f6?w=800"],
        "parsed_data": {"basis": {"merk": "Toyota", "model": "HiAce Reimo", "bouwjaar": 1998, "kilometerstand": 245000, "kenteken": None}, "capaciteit": {"slaapplaatsen": 2, "zitplaatsen": 4, "vaste_bedden": 0, "opklap_bedden": 2}, "technisch": {"brandstof": "benzine", "transmissie": "handgeschakeld", "vermogen_PK": 90, "lengte_cm": 470}, "comfort": {"airco": False, "GPS": False, "parkeersensoren": False}, "camper": {"keuken": True, "koelkast": False, "douche": False, "toilet": False}, "onderhoud": {"APK_geldig": True, "service_historie": False}}
    },
    {
        "marktplaats_id": "m2189012345",
        "title": "Sunliving S70SP - 2021 - Enkele bedden - Garage",
        "price": 5800000,
        "location": "Amersfoort",
        "url": "https://www.marktplaats.nl/v/campers-caravans/campers-bussen/m2189012345-sunliving-s70sp",
        "raw_html": "Sunliving S70SP met enkele bedden en grote garage. Fiat Ducato 140 PK, handgeschakeld. Ruim interieur, apart toilet, douche, L-vormige keuken. Zeer nette staat, 1e eigenaar.",
        "image_urls": ["https://images.unsplash.com/photo-1532274402911-5a369e4c4bb5?w=800", "https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=800", "https://images.unsplash.com/photo-1530789253388-582c481c54b0?w=800"],
        "parsed_data": {"basis": {"merk": "Sunliving", "model": "S70SP", "bouwjaar": 2021, "kilometerstand": 31000, "kenteken": None}, "capaciteit": {"slaapplaatsen": 4, "zitplaatsen": 4, "vaste_bedden": 2, "opklap_bedden": 2}, "technisch": {"brandstof": "diesel", "transmissie": "handgeschakeld", "vermogen_PK": 140, "lengte_cm": 740}, "comfort": {"airco": True, "GPS": False, "parkeersensoren": True}, "camper": {"keuken": True, "koelkast": True, "douche": True, "toilet": True}, "onderhoud": {"APK_geldig": True, "service_historie": True}}
    },
    {
        "marktplaats_id": "m2190123456",
        "title": "Opel Movano - Dreamer D55 - 2017 - Compact",
        "price": 3400000,
        "location": "Enschede",
        "url": "https://www.marktplaats.nl/v/campers-caravans/campers-bussen/m2190123456-opel-movano-dreamer-d55",
        "raw_html": "Dreamer D55 op Opel Movano. Compacte buscamper, makkelijk te rijden. Vast bed, keuken, koelkast. Geen douche/toilet. 145 PK handgeschakeld. Prima staat, alles werkt.",
        "image_urls": ["https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=800", "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=800"],
        "parsed_data": {"basis": {"merk": "Opel", "model": "Movano Dreamer D55", "bouwjaar": 2017, "kilometerstand": 88000, "kenteken": None}, "capaciteit": {"slaapplaatsen": 2, "zitplaatsen": 2, "vaste_bedden": 2, "opklap_bedden": 0}, "technisch": {"brandstof": "diesel", "transmissie": "handgeschakeld", "vermogen_PK": 145, "lengte_cm": 599}, "comfort": {"airco": True, "GPS": False, "parkeersensoren": False}, "camper": {"keuken": True, "koelkast": True, "douche": False, "toilet": False}, "onderhoud": {"APK_geldig": True, "service_historie": True}}
    },
    {
        "marktplaats_id": "m2201234567",
        "title": "Carado V337 Europa Edition - 2023 - Als nieuw",
        "price": 6800000,
        "location": "Almere",
        "url": "https://www.marktplaats.nl/v/campers-caravans/campers-bussen/m2201234567-carado-v337-europa-edition",
        "raw_html": "Carado V337 Europa Edition, bijna nieuw! Slechts 8.000 km. Fiat Ducato 140 PK automaat. Lengtebedden, keuken, douche/toilet, airco, navigatie. Garantie tot 2026. Niet-roker.",
        "image_urls": ["https://images.unsplash.com/photo-1540202404-a2f29016b523?w=800", "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800"],
        "parsed_data": {"basis": {"merk": "Carado", "model": "V337 Europa Edition", "bouwjaar": 2023, "kilometerstand": 8000, "kenteken": None}, "capaciteit": {"slaapplaatsen": 2, "zitplaatsen": 4, "vaste_bedden": 2, "opklap_bedden": 0}, "technisch": {"brandstof": "diesel", "transmissie": "automaat", "vermogen_PK": 140, "lengte_cm": 636}, "comfort": {"airco": True, "GPS": True, "parkeersensoren": True}, "camper": {"keuken": True, "koelkast": True, "douche": True, "toilet": True}, "onderhoud": {"APK_geldig": True, "service_historie": True}}
    },
]


def main():
    conn = sqlite3.connect(DB_PATH)
    
    # Ensure schema
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS campers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marktplaats_id TEXT UNIQUE,
            title TEXT,
            price INTEGER,
            location TEXT,
            url TEXT,
            raw_html TEXT,
            image_urls TEXT,
            parsed_data TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camper_id INTEGER NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (camper_id) REFERENCES campers(id) ON DELETE CASCADE
        );
    """)

    inserted = 0
    for c in CAMPERS:
        try:
            conn.execute(
                """INSERT OR REPLACE INTO campers
                   (marktplaats_id, title, price, location, url, raw_html, image_urls, parsed_data)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    c["marktplaats_id"],
                    c["title"],
                    c["price"],
                    c["location"],
                    c["url"],
                    c["raw_html"],
                    json.dumps(c["image_urls"]),
                    json.dumps(c["parsed_data"], ensure_ascii=False),
                ),
            )
            inserted += 1
        except Exception as e:
            print(f"Error inserting {c['title']}: {e}")

    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM campers").fetchone()[0]
    conn.close()

    print(f"✅ Inserted {inserted} campers. Total in DB: {total}")


if __name__ == "__main__":
    main()
