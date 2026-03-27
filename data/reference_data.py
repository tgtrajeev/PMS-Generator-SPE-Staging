"""
Reference data tables for PMS Generator.
Contains ASME standards data, material properties, and industry reference tables.
"""

# ============================================================
# MATERIAL PROPERTIES - Allowable Stress (psi) at Temperature
# Source: ASME B31.3 Table A-1
# ============================================================
ALLOWABLE_STRESS = {
    # Carbon Steel
    "A106 Gr.B": {
        -29: 20000, 38: 20000, 93: 20000, 149: 20000, 204: 20000,
        260: 20000, 316: 18900, 343: 18200, 371: 17300, 399: 15600,
        427: 13000, 454: 10800, 482: 8700,
        "spec": "ASTM A106", "type": "CS", "smts": 60000, "smys": 35000,
    },
    "A53 Gr.B": {
        -29: 20000, 38: 20000, 93: 20000, 149: 20000, 204: 20000,
        260: 20000, 316: 18900, 343: 18200, 371: 17300,
        "spec": "ASTM A53", "type": "CS", "smts": 60000, "smys": 35000,
    },
    "A333 Gr.6": {
        -46: 20000, -29: 20000, 38: 20000, 93: 20000, 149: 20000,
        204: 20000, 260: 20000, 316: 18900, 343: 18200,
        "spec": "ASTM A333", "type": "CS-LT", "smts": 60000, "smys": 35000,
    },
    # Stainless Steel
    "A312 TP304": {
        -198: 20000, -29: 20000, 38: 20000, 93: 20000, 149: 18100,
        204: 16600, 260: 15400, 316: 14400, 343: 14000, 371: 13700,
        399: 13400, 427: 13200, 454: 13000, 482: 12900, 510: 12700,
        538: 12400, 566: 11900, 593: 11200, 621: 10200, 649: 8900,
        "spec": "ASTM A312", "type": "SS", "smts": 75000, "smys": 30000,
    },
    "A312 TP316": {
        -198: 20000, -29: 20000, 38: 20000, 93: 20000, 149: 19000,
        204: 17500, 260: 16300, 316: 15300, 343: 14900, 371: 14600,
        399: 14300, 427: 14100, 454: 13900, 482: 13800, 510: 13600,
        538: 13300, 566: 12800, 593: 12100, 621: 11100, 649: 9800,
        "spec": "ASTM A312", "type": "SS", "smts": 75000, "smys": 30000,
    },
    # Alloy Steel
    "A335 P11": {
        -29: 17100, 38: 17100, 93: 17100, 149: 17100, 204: 17100,
        260: 17100, 316: 17100, 343: 17100, 371: 17100, 399: 16900,
        427: 16200, 454: 14800, 482: 12800, 510: 10200, 538: 7800,
        "spec": "ASTM A335", "type": "Alloy", "smts": 60000, "smys": 30000,
    },
    "A335 P22": {
        -29: 20000, 38: 20000, 93: 20000, 149: 20000, 204: 20000,
        260: 20000, 316: 20000, 343: 20000, 371: 20000, 399: 19400,
        427: 18200, 454: 16500, 482: 14200, 510: 11500, 538: 8900,
        566: 6500, 593: 4500,
        "spec": "ASTM A335", "type": "Alloy", "smts": 60000, "smys": 30000,
    },
}

# ============================================================
# PIPE DIMENSIONS - OD and Wall Thickness per ASME B36.10 (CS) & B36.19 (SS)
# Dimensions in inches
# ============================================================
PIPE_DIMENSIONS_B36_10 = {
    # NPS: (OD, {Schedule: Wall Thickness in inches})
    # Source: ASME B36.10M-2018.
    # "Std" (Standard Wall): = Sch 40 for NPS ≤ 10"; = 0.375" for NPS ≥ 12".
    # "XS"  (Extra Strong):  = Sch 80 for NPS ≤ 8";  = 0.500" for NPS ≥ 10".
    "0.5":  (0.840, {"5S": 0.065, "10S": 0.083, "Std": 0.109, "40": 0.109, "80": 0.147, "XS": 0.147, "160": 0.294, "XXS": 0.294}),
    "0.75": (1.050, {"5S": 0.065, "10S": 0.083, "Std": 0.113, "40": 0.113, "80": 0.154, "XS": 0.154, "160": 0.219, "XXS": 0.308}),
    "1":    (1.315, {"5S": 0.065, "10S": 0.109, "Std": 0.133, "40": 0.133, "80": 0.179, "XS": 0.179, "160": 0.250, "XXS": 0.358}),
    "1.25": (1.660, {"5S": 0.065, "10S": 0.109, "Std": 0.140, "40": 0.140, "80": 0.191, "XS": 0.191, "160": 0.250, "XXS": 0.382}),
    "1.5":  (1.900, {"5S": 0.065, "10S": 0.109, "Std": 0.145, "40": 0.145, "80": 0.200, "XS": 0.200, "160": 0.281, "XXS": 0.400}),
    "2":    (2.375, {"5S": 0.065, "10S": 0.109, "Std": 0.154, "40": 0.154, "80": 0.218, "XS": 0.218, "160": 0.344, "XXS": 0.436}),
    "3":    (3.500, {"5S": 0.083, "10S": 0.120, "Std": 0.216, "40": 0.216, "80": 0.300, "XS": 0.300, "160": 0.438, "XXS": 0.600}),
    "4":    (4.500, {"5S": 0.083, "10S": 0.120, "Std": 0.237, "40": 0.237, "80": 0.337, "XS": 0.337, "120": 0.438, "160": 0.531, "XXS": 0.674}),
    "6":    (6.625, {"5S": 0.109, "10S": 0.134, "Std": 0.280, "40": 0.280, "80": 0.432, "XS": 0.432, "120": 0.562, "160": 0.719, "XXS": 0.864}),
    "8":    (8.625, {"5S": 0.109, "10S": 0.148, "20": 0.250, "30": 0.277, "Std": 0.322, "40": 0.322, "60": 0.406, "80": 0.500, "XS": 0.500, "100": 0.594, "120": 0.719, "140": 0.812, "160": 0.906, "XXS": 0.875}),
    "10":   (10.750, {"5S": 0.134, "10S": 0.165, "20": 0.250, "30": 0.307, "Std": 0.365, "40": 0.365, "XS": 0.500, "60": 0.500, "80": 0.594, "100": 0.719, "120": 0.844, "140": 1.000, "160": 1.125}),
    "12":   (12.750, {"5S": 0.156, "10S": 0.180, "20": 0.250, "30": 0.330, "Std": 0.375, "XS": 0.500, "40": 0.406, "60": 0.562, "80": 0.688, "100": 0.844, "120": 1.000, "140": 1.125, "160": 1.312}),
    "14":   (14.000, {"5S": 0.156, "10S": 0.188, "10": 0.250, "20": 0.312, "Std": 0.375, "30": 0.375, "XS": 0.500, "40": 0.438, "60": 0.594, "80": 0.750, "100": 0.938, "120": 1.094, "140": 1.250, "160": 1.406}),
    "16":   (16.000, {"5S": 0.165, "10S": 0.188, "10": 0.250, "20": 0.312, "Std": 0.375, "30": 0.375, "40": 0.500, "XS": 0.500, "60": 0.656, "80": 0.844, "100": 1.031, "120": 1.219, "140": 1.438, "160": 1.594}),
    "18":   (18.000, {"5S": 0.165, "10S": 0.188, "10": 0.250, "20": 0.312, "Std": 0.375, "30": 0.438, "XS": 0.500, "40": 0.562, "60": 0.750, "80": 0.938, "100": 1.156, "120": 1.375, "140": 1.562, "160": 1.781}),
    "20":   (20.000, {"5S": 0.188, "10S": 0.218, "10": 0.250, "20": 0.375, "Std": 0.375, "30": 0.500, "XS": 0.500, "40": 0.594, "60": 0.812, "80": 1.031, "100": 1.281, "120": 1.500, "140": 1.750, "160": 1.969}),
    "22":   (22.000, {"10": 0.250, "20": 0.375, "Std": 0.375, "XS": 0.500, "30": 0.500, "60": 0.875, "80": 1.125}),
    "24":   (24.000, {"5S": 0.218, "10S": 0.250, "10": 0.250, "20": 0.375, "Std": 0.375, "XS": 0.500, "30": 0.562, "40": 0.688, "60": 0.969, "80": 1.219, "100": 1.531, "120": 1.812, "140": 2.062, "160": 2.344}),
    "26":   (26.000, {"10": 0.312, "Std": 0.375, "20": 0.500, "XS": 0.500}),
    "28":   (28.000, {"10": 0.312, "Std": 0.375, "20": 0.500, "XS": 0.500, "30": 0.625}),
    "30":   (30.000, {"5S": 0.250, "10S": 0.312, "10": 0.312, "Std": 0.375, "20": 0.500, "XS": 0.500, "30": 0.625, "40": 0.750}),
    "32":   (32.000, {"10": 0.312, "Std": 0.375, "20": 0.500, "XS": 0.500, "30": 0.625, "40": 0.688}),
    "36":   (36.000, {"5S": 0.312, "10S": 0.312, "10": 0.312, "Std": 0.375, "20": 0.500, "XS": 0.500, "30": 0.625, "40": 0.750}),
    "42":   (42.000, {"10": 0.312, "Std": 0.375, "20": 0.500, "XS": 0.500, "30": 0.625, "40": 0.750}),
    "48":   (48.000, {"10": 0.312, "Std": 0.375, "20": 0.500, "XS": 0.500, "30": 0.625, "40": 0.750}),
}

# B36.19 uses same OD but different schedules for SS
PIPE_DIMENSIONS_B36_19 = {
    "0.5":  (0.840,  {"5S": 0.065, "10S": 0.083, "40S": 0.109, "80S": 0.147}),
    "0.75": (1.050,  {"5S": 0.065, "10S": 0.083, "40S": 0.113, "80S": 0.154}),
    "1":    (1.315,  {"5S": 0.065, "10S": 0.109, "40S": 0.133, "80S": 0.179}),
    "1.25": (1.660,  {"5S": 0.065, "10S": 0.109, "40S": 0.140, "80S": 0.191}),
    "1.5":  (1.900,  {"5S": 0.065, "10S": 0.109, "40S": 0.145, "80S": 0.200}),
    "2":    (2.375,  {"5S": 0.065, "10S": 0.109, "40S": 0.154, "80S": 0.218}),
    "3":    (3.500,  {"5S": 0.083, "10S": 0.120, "40S": 0.216, "80S": 0.300}),
    "4":    (4.500,  {"5S": 0.083, "10S": 0.120, "40S": 0.237, "80S": 0.337}),
    "6":    (6.625,  {"5S": 0.109, "10S": 0.134, "40S": 0.280, "80S": 0.432}),
    "8":    (8.625,  {"5S": 0.109, "10S": 0.148, "40S": 0.322, "80S": 0.500}),
    "10":   (10.750, {"5S": 0.134, "10S": 0.165, "40S": 0.365, "80S": 0.500}),
    "12":   (12.750, {"5S": 0.156, "10S": 0.180, "40S": 0.375, "80S": 0.500}),
    "14":   (14.000, {"5S": 0.156, "10S": 0.188}),
    "16":   (16.000, {"5S": 0.165, "10S": 0.188}),
    "18":   (18.000, {"5S": 0.165, "10S": 0.188}),
    "20":   (20.000, {"5S": 0.188, "10S": 0.218}),
    "24":   (24.000, {"5S": 0.218, "10S": 0.250}),
}

# ============================================================
# FLANGE RATINGS - Pressure-Temperature Ratings (psig)
# Classes 150–2500: ASME B16.5 Group 1.1 (CS A105) / Group 2.1 (SS 316)
# Classes 5000–10000: API 6A Table 3 (Wellhead Equipment)
# ============================================================
FLANGE_RATINGS_CS = {
    # ASME B16.5-2020, Table 2-1.1 (Group 1.1: A105/A216 WCB/A106 Gr.B)
    # Temperature (°F): {Class: Max Allowable Working Pressure (psig)}
    # Classes 5000 & 10000 per API 6A
    -20:  {150: 285, 300: 740, 400: 990, 600: 1480, 900: 2220, 1500: 3705, 2500: 6170, 5000: 5000,  10000: 10000},
    100:  {150: 285, 300: 740, 400: 990, 600: 1480, 900: 2220, 1500: 3705, 2500: 6170, 5000: 5000,  10000: 10000},
    200:  {150: 260, 300: 675, 400: 900, 600: 1350, 900: 2025, 1500: 3375, 2500: 5625, 5000: 4900,  10000: 9800},
    300:  {150: 230, 300: 655, 400: 875, 600: 1315, 900: 1970, 1500: 3280, 2500: 5470, 5000: 4700,  10000: 9400},
    400:  {150: 200, 300: 635, 400: 845, 600: 1270, 900: 1900, 1500: 3170, 2500: 5280, 5000: 4350,  10000: 8700},
    500:  {150: 170, 300: 600, 400: 800, 600: 1200, 900: 1795, 1500: 2995, 2500: 4990, 5000: 3900,  10000: 7800},
    600:  {150: 140, 300: 550, 400: 730, 600: 1095, 900: 1640, 1500: 2735, 2500: 4560, 5000: 3350,  10000: 6700},
    650:  {150: 125, 300: 535, 400: 715, 600: 1075, 900: 1610, 1500: 2685, 2500: 4475, 5000: 3050,  10000: 6100},
    700:  {150: 110, 300: 535, 400: 710, 600: 1065, 900: 1600, 1500: 2665, 2500: 4440, 5000: 2750,  10000: 5500},
    750:  {150: 95,  300: 505, 400: 670, 600: 1010, 900: 1510, 1500: 2520, 2500: 4200, 5000: 2450,  10000: 4900},
    800:  {150: 80,  300: 410, 400: 550, 600: 825,  900: 1235, 1500: 2060, 2500: 3430, 5000: 2150,  10000: 4300},
}

FLANGE_RATINGS_SS = {
    # ASME B16.5-2020, Table 2-2.3 (Group 2.3: A182 F316/F316L, A351 CF8M)
    # Temperature (°F): {Class: Max Allowable Working Pressure (psig)}
    # Classes 5000 & 10000 per API 6A
    -20:  {150: 275, 300: 720, 400: 960,  600: 1440, 900: 2160, 1500: 3600, 2500: 6000, 5000: 5000,  10000: 10000},
    100:  {150: 275, 300: 720, 400: 960,  600: 1440, 900: 2160, 1500: 3600, 2500: 6000, 5000: 5000,  10000: 10000},
    200:  {150: 240, 300: 620, 400: 825,  600: 1240, 900: 1860, 1500: 3100, 2500: 5170, 5000: 4950,  10000: 9900},
    300:  {150: 220, 300: 570, 400: 760,  600: 1140, 900: 1710, 1500: 2850, 2500: 4750, 5000: 4750,  10000: 9500},
    400:  {150: 200, 300: 540, 400: 720,  600: 1075, 900: 1615, 1500: 2690, 2500: 4480, 5000: 4500,  10000: 9000},
    500:  {150: 185, 300: 515, 400: 685,  600: 1030, 900: 1545, 1500: 2575, 2500: 4290, 5000: 4200,  10000: 8400},
    600:  {150: 170, 300: 500, 400: 665,  600: 1000, 900: 1495, 1500: 2495, 2500: 4155, 5000: 3900,  10000: 7800},
    700:  {150: 155, 300: 480, 400: 640,  600: 960,  900: 1440, 1500: 2395, 2500: 3995, 5000: 3600,  10000: 7200},
    800:  {150: 145, 300: 470, 400: 625,  600: 935,  900: 1405, 1500: 2340, 2500: 3900, 5000: 3350,  10000: 6700},
    900:  {150: 135, 300: 465, 400: 615,  600: 930,  900: 1395, 1500: 2325, 2500: 3870, 5000: 3100,  10000: 6200},
    1000: {150: 125, 300: 455, 400: 605,  600: 910,  900: 1365, 1500: 2270, 2500: 3785, 5000: 2850,  10000: 5700},
}

# ============================================================
# FLANGE RATINGS - METRIC (bar at °C) per ASME B16.5-2020
# Use these for Excel P-T output to match industry standard metric tables
# ============================================================
FLANGE_RATINGS_CS_METRIC = {
    # ASME B16.5-2020, Table 2-1.1 METRIC (Group 1.1: A105/A216 WCB/A106 Gr.B)
    # Temperature (°C): {Class: Max Allowable Working Pressure (bar)}
    -29: {150: 19.6, 300: 51.0, 400: 68.3, 600: 102.1, 900: 153.1, 1500: 255.5, 2500: 425.4},
     38: {150: 19.6, 300: 51.0, 400: 68.3, 600: 102.1, 900: 153.1, 1500: 255.5, 2500: 425.4},
     50: {150: 19.2, 300: 50.1, 400: 66.9, 600: 100.0, 900: 150.1, 1500: 250.2, 2500: 417.1},
    100: {150: 17.7, 300: 46.6, 400: 62.1, 600: 93.2, 900: 139.6, 1500: 232.7, 2500: 387.8},
    150: {150: 15.8, 300: 45.1, 400: 60.3, 600: 90.7, 900: 135.8, 1500: 226.2, 2500: 377.1},
    200: {150: 13.8, 300: 43.8, 400: 58.3, 600: 87.6, 900: 131.0, 1500: 218.5, 2500: 364.1},
    250: {150: 12.1, 300: 41.4, 400: 55.2, 600: 82.7, 900: 123.8, 1500: 206.5, 2500: 344.1},
    300: {150: 10.2, 300: 37.9, 400: 50.3, 600: 75.5, 900: 113.1, 1500: 188.6, 2500: 314.4},
    350: {150: 8.6,  300: 36.9, 400: 49.3, 600: 74.1, 900: 111.0, 1500: 185.1, 2500: 308.6},
    375: {150: 7.6,  300: 36.9, 400: 49.0, 600: 73.4, 900: 110.3, 1500: 183.8, 2500: 306.2},
    400: {150: 6.5,  300: 34.8, 400: 46.2, 600: 69.6, 900: 104.1, 1500: 173.8, 2500: 289.6},
    425: {150: 5.5,  300: 28.3, 400: 37.9, 600: 56.9, 900: 85.2,  1500: 142.0, 2500: 236.5},
}

FLANGE_RATINGS_SS_METRIC = {
    # ASME B16.5-2020, Table 2-2.3 METRIC (Group 2.3: A182 F316/F316L, A351 CF8M)
    -29: {150: 19.0, 300: 49.6, 400: 66.2, 600: 99.3, 900: 148.9, 1500: 248.2, 2500: 413.7},
     38: {150: 19.0, 300: 49.6, 400: 66.2, 600: 99.3, 900: 148.9, 1500: 248.2, 2500: 413.7},
     50: {150: 18.5, 300: 48.1, 400: 64.2, 600: 96.4, 900: 144.5, 1500: 240.6, 2500: 401.3},
    100: {150: 16.5, 300: 42.8, 400: 56.9, 600: 85.5, 900: 128.3, 1500: 213.7, 2500: 356.5},
    150: {150: 15.2, 300: 39.3, 400: 52.4, 600: 78.6, 900: 117.9, 1500: 196.5, 2500: 327.5},
    200: {150: 13.8, 300: 37.2, 400: 49.6, 600: 74.1, 900: 111.3, 1500: 185.5, 2500: 308.9},
    250: {150: 12.8, 300: 35.5, 400: 47.2, 600: 71.0, 900: 106.5, 1500: 177.5, 2500: 295.8},
    300: {150: 11.7, 300: 34.5, 400: 45.8, 600: 69.0, 900: 103.1, 1500: 172.0, 2500: 286.5},
    350: {150: 10.7, 300: 33.1, 400: 44.1, 600: 66.2, 900: 99.3,  1500: 165.2, 2500: 275.5},
    400: {150: 10.0, 300: 32.4, 400: 43.1, 600: 64.5, 900: 96.9,  1500: 161.3, 2500: 268.9},
    450: {150: 9.3,  300: 32.1, 400: 42.4, 600: 64.1, 900: 96.2,  1500: 160.3, 2500: 266.9},
    500: {150: 8.6,  300: 31.4, 400: 41.7, 600: 62.8, 900: 94.1,  1500: 156.5, 2500: 261.0},
    538: {150: 8.3,  300: 30.0, 400: 40.0, 600: 60.0, 900: 90.0,  1500: 150.0, 2500: 250.0},
}

# Standard OD values in mm (exact metric per ASME B36.10M/B36.19M)
STANDARD_OD_MM = {
    "0.5": 21.3, "0.75": 26.7, "1": 33.4, "1.25": 42.2, "1.5": 48.3,
    "2": 60.3, "3": 88.9, "4": 114.3, "6": 168.3, "8": 219.1,
    "10": 273.1, "12": 323.9, "14": 355.6, "16": 406.4, "18": 457,
    "20": 508, "22": 559, "24": 610, "26": 660, "28": 711, "30": 762,
    "36": 914.4, "42": 1066.8, "48": 1219.2,
}

# ============================================================
# SPECIFICATION CODE MAPPING
# Maps material type + corrosion allowance to spec codes
# ============================================================
SPEC_CODE_MAP = {
    # Carbon Steel
    ("CS", 0.0):  "A3",      # CS, No CA, Non-corrosive
    ("CS", 1.0):  "A1",      # CS, 1.0mm CA, Mild
    ("CS", 1.5):  "A1",      # CS, 1.5mm CA, General Service
    ("CS", 2.0):  "A1A",     # CS, 2.0mm CA, Moderate
    ("CS", 3.0):  "A2",      # CS, 3.0mm CA, Corrosive Service
    ("CS", 4.5):  "A2A",     # CS, 4.5mm CA, Severe Service
    ("CS", 6.0):  "A4",      # CS, 6.0mm CA, Highly Corrosive
    # Carbon Steel Low Temperature
    ("CS-LT", 0.0):  "A3LN", # CS-LT, No CA
    ("CS-LT", 1.5):  "A1LN", # CS-LT, 1.5mm CA
    ("CS-LT", 3.0):  "A2LN", # CS-LT, 3.0mm CA
    ("CS-LT", 6.0):  "A4LN", # CS-LT, 6.0mm CA, Highly Corrosive
    # Stainless Steel
    ("SS", 0.0):  "S1",      # SS, No CA
    ("SS", 1.5):  "S2",      # SS, 1.5mm CA
    ("SS", 3.0):  "D1",      # SS, 3.0mm CA, Corrosive
    # Alloy Steel
    ("Alloy", 0.0): "B1",    # Alloy, No CA
    ("Alloy", 1.5): "B2",    # Alloy, 1.5mm CA
    ("Alloy", 3.0): "B3",    # Alloy, 3.0mm CA
}

# ============================================================
# FITTING MATERIALS - Maps pipe material to fitting specs
# ============================================================
FITTING_MATERIALS = {
    "A106 Gr.B":   {"elbow": "A234 WPB",  "tee": "A234 WPB",  "reducer": "A234 WPB",  "cap": "A234 WPB"},
    "A53 Gr.B":    {"elbow": "A234 WPB",  "tee": "A234 WPB",  "reducer": "A234 WPB",  "cap": "A234 WPB"},
    "A333 Gr.6":   {"elbow": "A420 WPL6", "tee": "A420 WPL6", "reducer": "A420 WPL6", "cap": "A420 WPL6"},
    "A312 TP304":  {"elbow": "A403 WP304","tee": "A403 WP304","reducer": "A403 WP304","cap": "A403 WP304"},
    "A312 TP316":  {"elbow": "A403 WP316","tee": "A403 WP316","reducer": "A403 WP316","cap": "A403 WP316"},
    "A335 P11":    {"elbow": "A234 WP11", "tee": "A234 WP11", "reducer": "A234 WP11", "cap": "A234 WP11"},
    "A335 P22":    {"elbow": "A234 WP22", "tee": "A234 WP22", "reducer": "A234 WP22", "cap": "A234 WP22"},
}

# ============================================================
# FLANGE MATERIALS - Maps pipe material to flange specs
# ============================================================
FLANGE_MATERIALS = {
    "A106 Gr.B":  {"flange": "A105",      "type": "WN/SO/BL"},
    "A53 Gr.B":   {"flange": "A105",      "type": "WN/SO/BL"},
    "A333 Gr.6":  {"flange": "A350 LF2",  "type": "WN/SO/BL"},
    "A312 TP304": {"flange": "A182 F304", "type": "WN/SO/BL"},
    "A312 TP316": {"flange": "A182 F316", "type": "WN/SO/BL"},
    "A335 P11":   {"flange": "A182 F11",  "type": "WN/SO/BL"},
    "A335 P22":   {"flange": "A182 F22",  "type": "WN/SO/BL"},
}

# ============================================================
# GASKET MATERIALS
# ============================================================
GASKET_MATERIALS = {
    "CS":     {"type": "Spiral Wound", "material": "CS/Graphite",   "spec": "ASME B16.20", "inner": "CS", "filler": "Graphite"},
    "CS-LT":  {"type": "Spiral Wound", "material": "CS/Graphite",   "spec": "ASME B16.20", "inner": "CS", "filler": "Graphite"},
    "SS":     {"type": "Spiral Wound", "material": "SS304/Graphite","spec": "ASME B16.20", "inner": "SS304", "filler": "Graphite/PTFE"},
    "Alloy":  {"type": "Spiral Wound", "material": "Alloy/Graphite","spec": "ASME B16.20", "inner": "Alloy Steel", "filler": "Graphite"},
}

# ============================================================
# BOLTING MATERIALS
# ============================================================
_COAT = ", XYLAR 2 + XYLAN 1070 coated with minimum combined thickness of 50\u03bcm"
BOLTING_MATERIALS = {
    "CS":     {"stud": "ASTM A 193 Gr. B7M" + _COAT,       "nut": "ASTM A 194 Gr. 2HM" + _COAT,  "temp_range": "-29 to 400 degC"},
    "CS-LT":  {"stud": "ASTM A 320 Gr. L7",                 "nut": "ASTM A 194 Gr. 7",             "temp_range": "-101 to 400 degC"},
    "SS":     {"stud": "ASTM A 193 Gr. B8M Class 2",        "nut": "ASTM A 194 Gr. 8M",            "temp_range": "-198 to 800 degC"},
    "Alloy":  {"stud": "ASTM A 193 Gr. B7",                 "nut": "ASTM A 194 Gr. 2H",            "temp_range": "-29 to 540 degC"},
}

# ============================================================
# VALVE TYPES AND MATERIALS
# ============================================================
VALVE_MATERIALS = {
    "CS": {
        "Gate":       {"body": "A216 WCB", "trim": "13Cr/Stellite", "seat": "13Cr"},
        "Globe":      {"body": "A216 WCB", "trim": "13Cr/Stellite", "seat": "13Cr"},
        "Check":      {"body": "A216 WCB", "trim": "13Cr",         "seat": "13Cr"},
        "Ball":       {"body": "A216 WCB", "trim": "SS316",        "seat": "PTFE/RPTFE"},
        "Butterfly":  {"body": "A216 WCB", "trim": "SS316",        "seat": "EPDM/PTFE"},
        "Needle":     {"body": "A105",     "trim": "SS316",        "seat": "PEEK"},
        "DBB":        {"body": "A216 WCB", "trim": "SS316",        "seat": "PEEK"},
    },
    "CS-LT": {
        "Gate":       {"body": "A352 LCB", "trim": "13Cr/Stellite", "seat": "13Cr"},
        "Globe":      {"body": "A352 LCB", "trim": "13Cr/Stellite", "seat": "13Cr"},
        "Check":      {"body": "A352 LCB", "trim": "13Cr",         "seat": "13Cr"},
        "Ball":       {"body": "A352 LCB", "trim": "SS316",        "seat": "PTFE/RPTFE"},
        "Needle":     {"body": "A350 LF2", "trim": "SS316",        "seat": "PEEK"},
        "DBB":        {"body": "A352 LCB", "trim": "SS316",        "seat": "PEEK"},
    },
    "SS": {
        "Gate":       {"body": "A351 CF8M", "trim": "Stellite",     "seat": "Stellite"},
        "Globe":      {"body": "A351 CF8M", "trim": "Stellite",     "seat": "Stellite"},
        "Check":      {"body": "A351 CF8M", "trim": "SS316",       "seat": "SS316"},
        "Ball":       {"body": "A351 CF8M", "trim": "SS316",       "seat": "PTFE/RPTFE"},
        "Needle":     {"body": "A182 F316", "trim": "SS316",       "seat": "PEEK"},
        "DBB":        {"body": "A351 CF8M", "trim": "SS316",       "seat": "PEEK"},
    },
    "Alloy": {
        "Gate":       {"body": "A217 WC6",  "trim": "Stellite",     "seat": "Stellite"},
        "Globe":      {"body": "A217 WC6",  "trim": "Stellite",     "seat": "Stellite"},
        "Check":      {"body": "A217 WC6",  "trim": "Stellite",     "seat": "Stellite"},
        "Needle":     {"body": "A182 F11",  "trim": "Stellite",    "seat": "PEEK"},
        "DBB":        {"body": "A217 WC6",  "trim": "Stellite",    "seat": "PEEK"},
    },
}

# VDS (Valve Data Sheet) structured code mappings
# Format: [Type 2-char][Bore/Design 1-char][Seat 1-char][Spec Code][End Conn 1-char]
# Example: GAYMA1R = Gate + Screw&Yoke + Metal + A1 + Raised Face
VDS_VALVE_TYPE_CODES = {
    "Ball": "BL", "Butterfly": "BF", "Gate": "GA", "Globe": "GL",
    "Check": "CH", "Needle": "NE", "DBB": "DB",
}

VDS_DESIGN_CODES = {
    "Ball": "R",       # Reduced Bore
    "Butterfly": "W",  # Wafer
    "Gate": "Y",       # Screw & Yoke
    "Globe": "Y",      # Screw & Yoke
    "Check": "P",      # Piston
    "Needle": "I",     # Inline Straight
    "DBB": "M",        # Modular (Ball, Needle, Ball)
}

VALVE_END_CONNECTIONS = {
    (150, "small"):  "Screwed (NPT) / Socket Weld",
    (150, "large"):  "Flanged RF",
    (300, "small"):  "Socket Weld",
    (300, "large"):  "Flanged RF",
    (600, "small"):  "Socket Weld / Butt Weld",
    (600, "large"):  "Flanged RF / Butt Weld",
    (900, "small"):  "Butt Weld",
    (900, "large"):  "Flanged RF / Butt Weld",
    (1500, "small"): "Butt Weld",
    (1500, "large"): "Flanged RTJ / Butt Weld",
    (2500, "small"): "Butt Weld",
    (2500, "large"): "Flanged RTJ",
}

# Joint efficiency factors (ASME B31.3)
JOINT_EFFICIENCY = {
    "seamless": 1.0,
    "ERW": 0.85,
    "SAW": 0.85,
    "DSAW": 1.0,
    "furnace_butt_weld": 0.60,
}

# Branch connection types based on size ratio
BRANCH_CONNECTIONS = {
    "equal":   "Butt Weld Tee",
    "1_size":  "Reducing Tee",
    "2_size":  "Weldolet",
    "3_plus":  "Weldolet / Sockolet",
}

# Corrosion Allowance typical values (mm)
TYPICAL_CA = {
    "CS":    {"non_corrosive": 1.5, "mildly_corrosive": 3.0, "corrosive": 6.0},
    "CS-LT": {"non_corrosive": 1.5, "mildly_corrosive": 3.0, "corrosive": 6.0},
    "SS":    {"non_corrosive": 0.0, "mildly_corrosive": 0.0, "corrosive": 1.5},
    "Alloy": {"non_corrosive": 0.0, "mildly_corrosive": 1.5, "corrosive": 3.0},
}

# ============================================================
# ASME B16.11 - Socket Weld & Threaded Fittings
# ============================================================
SOCKET_WELD_FITTINGS_B16_11 = {
    "CS":    {"3000#": "A105", "6000#": "A105"},
    "CS-LT": {"3000#": "A350 LF2", "6000#": "A350 LF2"},
    "SS":    {"3000#": "A182 F304/F316", "6000#": "A182 F304/F316"},
    "Alloy": {"3000#": "A182 F11/F22", "6000#": "A182 F11/F22"},
}

THREADED_FITTINGS_B16_11 = {
    "CS":    {"3000#": "A105", "6000#": "A105"},
    "CS-LT": {"3000#": "A350 LF2", "6000#": "A350 LF2"},
    "SS":    {"3000#": "A182 F304/F316", "6000#": "A182 F304/F316"},
    "Alloy": {"3000#": "A182 F11/F22", "6000#": "A182 F11/F22"},
}

SW_FITTING_TYPES = [
    "90 deg Elbow", "45 deg Elbow", "Tee", "Full Coupling",
    "Half Coupling", "Union", "Cap", "Plug", "Bushing",
]

# ============================================================
# ASME B16.25 - Buttwelding Ends
# ============================================================
BUTTWELD_END_PREP_B16_25 = {
    "standard_bevel": {
        "angle": "37.5 +/- 2.5 deg",
        "root_face": "1/16 in +/- 1/32 in",
        "root_gap": "1/16 in +/- 1/32 in",
    },
    "compound_bevel": {
        "inner_angle": "10 deg",
        "outer_angle": "37.5 deg",
        "transition_thickness": "3/4 in",
    },
}

# ============================================================
# ASME B16.47 - Large Diameter Steel Flanges (NPS 26-60)
# Series A (MSS SP-44) P-T Ratings (psig)
# ============================================================
FLANGE_RATINGS_B16_47 = {
    "CS": {
        -20:  {75: 140, 150: 285, 300: 740, 400: 990, 600: 1480, 900: 2220},
        100:  {75: 140, 150: 285, 300: 740, 400: 990, 600: 1480, 900: 2220},
        200:  {75: 130, 150: 260, 300: 680, 400: 905, 600: 1350, 900: 2025},
        300:  {75: 115, 150: 230, 300: 655, 400: 875, 600: 1315, 900: 1970},
        400:  {75: 100, 150: 200, 300: 635, 400: 845, 600: 1270, 900: 1900},
        500:  {75: 85,  150: 170, 300: 600, 400: 800, 600: 1200, 900: 1795},
        600:  {75: 70,  150: 140, 300: 550, 400: 730, 600: 1095, 900: 1640},
        700:  {75: 55,  150: 110, 300: 535, 400: 715, 600: 1065, 900: 1600},
        800:  {75: 40,  150: 80,  300: 410, 400: 550, 600: 825,  900: 1235},
    },
    "SS": {
        -20:  {75: 135, 150: 275, 300: 720, 400: 960, 600: 1440, 900: 2160},
        100:  {75: 135, 150: 275, 300: 720, 400: 960, 600: 1440, 900: 2160},
        200:  {75: 120, 150: 240, 300: 620, 400: 825, 600: 1240, 900: 1860},
        300:  {75: 108, 150: 215, 300: 570, 400: 760, 600: 1135, 900: 1705},
        400:  {75: 98,  150: 195, 300: 530, 400: 710, 600: 1060, 900: 1590},
        500:  {75: 88,  150: 175, 300: 505, 400: 675, 600: 1015, 900: 1520},
        600:  {75: 80,  150: 160, 300: 490, 400: 655, 600: 985,  900: 1475},
        700:  {75: 75,  150: 150, 300: 480, 400: 640, 600: 965,  900: 1445},
        800:  {75: 70,  150: 140, 300: 475, 400: 630, 600: 945,  900: 1420},
    },
}

B16_47_NPS_RANGE = ["26", "28", "30", "32", "34", "36", "40", "42", "48", "54", "60"]

# ============================================================
# ASME B16.48 - Line Blanks
# ============================================================
LINE_BLANKS_B16_48 = {
    "types": ["Spectacle Blind", "Spacer Ring", "Paddle Blind"],
    "materials": {
        "CS": "A516 Gr.70", "CS-LT": "A516 Gr.70 (IT)",
        "SS": "A240 TP304/TP316", "Alloy": "A387 Gr.11/22",
    },
    "ratings": [150, 300, 600, 900, 1500, 2500],
    "standard": "ASME B16.48",
}

# ============================================================
# GASKET TEMPERATURE LIMITS (degF) - for validation
# ============================================================
GASKET_TEMP_LIMITS = {
    "Spiral Wound/Graphite": 850, "Spiral Wound/PTFE": 450,
    "Spiral Wound": 850, "RTJ": 1000, "CAF": 500, "Sheet Graphite": 750,
}

# ============================================================
# MATERIAL-FLUID INCOMPATIBILITY - for validation warnings
# ============================================================
MATERIAL_FLUID_INCOMPATIBLE = {
    "CS": ["Caustic (>50%)", "HF Acid", "Chloride Solutions", "Strong Oxidizing Acids", "Nitric Acid"],
    "CS-LT": ["Caustic (>50%)", "HF Acid", "Chloride Solutions", "Strong Oxidizing Acids"],
    "SS": ["H2S (wet, NACE MR0175)", "HCl Acid", "Hot Caustic (>150F)", "Chloride SCC environments"],
    "Alloy": ["Strong Oxidizing Acids"],
}


# ============================================================
# UCS-66 IMPACT TEST EXEMPTION CURVES
# Source: ASME Section VIII Div 1, Figure UCS-66
# Referenced by ASME B31.3 for MDMT compliance
# Keys: governing_thickness_in -> min_exempt_temp_F
# ============================================================
UCS_66_CURVES = {
    "A": {0.394: 18, 0.500: 28, 0.625: 38, 0.750: 48, 1.000: 60, 1.250: 68, 1.500: 75, 2.000: 90, 2.500: 105, 3.000: 120},
    "B": {0.394: -20, 0.500: -10, 0.625: 0, 0.750: 10, 1.000: 25, 1.250: 32, 1.500: 40, 2.000: 55, 2.500: 68, 3.000: 80},
    "C": {0.394: -55, 0.500: -48, 0.625: -38, 0.750: -30, 1.000: -15, 1.250: -8, 1.500: 0, 2.000: 15, 2.500: 28, 3.000: 40},
    "D": {0.394: -55, 0.500: -55, 0.625: -55, 0.750: -55, 1.000: -48, 1.250: -42, 1.500: -35, 2.000: -22, 2.500: -10, 3.000: 0},
}

# Material grade -> UCS-66 curve assignment
# "exempt" = austenitic stainless steel, no impact testing required
MATERIAL_UCS66_CURVE = {
    "A106 Gr.B": "B",
    "A53 Gr.B": "B",
    "A333 Gr.6": "D",
    "A312 TP304": "exempt",
    "A312 TP316": "exempt",
    "A335 P11": "B",
    "A335 P22": "B",
    "A790 S31803": "exempt",
}


# ============================================================
# CORROSION ALLOWANCE RECOMMENDATIONS BY FLUID TYPE
# Typical industry ranges for engineering advisory
# ============================================================
CA_RECOMMENDATIONS = {
    "Process Water":    {"typical_mm": (1.5, 2.0), "note": "Treated water, mild corrosion"},
    "Cooling Water":    {"typical_mm": (1.5, 3.0), "note": "Open loop higher, closed loop lower"},
    "Seawater":         {"typical_mm": (3.0, 6.0), "note": "Highly corrosive, consider CRA"},
    "Steam":            {"typical_mm": (0.0, 1.5), "note": "Low corrosion, erosion concern at high velocity"},
    "Condensate":       {"typical_mm": (1.5, 3.0), "note": "CO2 corrosion potential"},
    "Crude Oil":        {"typical_mm": (1.5, 3.0), "note": "Depends on H2S/CO2 content"},
    "Natural Gas":      {"typical_mm": (1.0, 1.5), "note": "Dry gas minimal, sour gas higher"},
    "Caustic":          {"typical_mm": (1.5, 3.0), "note": "CS susceptible above 50% concentration"},
    "Acid":             {"typical_mm": (3.0, 6.0), "note": "Material dependent, consider CRA"},
    "Instrument Air":   {"typical_mm": (0.0, 0.0), "note": "No corrosion allowance needed"},
    "Nitrogen":         {"typical_mm": (0.0, 0.0), "note": "Inert, no corrosion"},
    "Diesel":           {"typical_mm": (1.0, 1.5), "note": "Mild service"},
    "Lube Oil":         {"typical_mm": (0.5, 1.0), "note": "Low corrosion"},
    "Fuel Gas":         {"typical_mm": (1.0, 1.5), "note": "Depends on moisture content"},
    "Hydrogen":         {"typical_mm": (0.0, 1.0), "note": "Consider HIC/SOHIC for CS"},
    "Ammonia":          {"typical_mm": (1.5, 3.0), "note": "SCC concern for CS, check hardness"},
}

# ============================================================
# PRESSURE RATING CODES
# Industry-standard single-letter codes for pressure classes
# ============================================================
PRESSURE_RATING_CODES = {
    "A": {"rating": "150#",   "pressure_psig": 150},
    "B": {"rating": "300#",   "pressure_psig": 300},
    "D": {"rating": "600#",   "pressure_psig": 600},
    "E": {"rating": "900#",   "pressure_psig": 900},
    "F": {"rating": "1500#",  "pressure_psig": 1500},
    "G": {"rating": "2500#",  "pressure_psig": 2500},
    "J": {"rating": "5000#",  "pressure_psig": 5000},
    "K": {"rating": "10000#", "pressure_psig": 10000},
    "T": {"rating": "Tubing", "pressure_psig": None},
}


# ============================================================
# PMS CODE PART 2 - Material + Corrosion Allowance Codes
# Each code encodes material type and CA
# ============================================================
PMS_MATERIAL_CODES = {
    1:  {"material_type": "CS",                "description": "CS-3mm CA",                             "ca_mm": 3.0},
    2:  {"material_type": "CS",                "description": "CS-6mm CA",                             "ca_mm": 6.0},
    3:  {"material_type": "CS GALV",           "description": "CS GALV-3mm CA",                        "ca_mm": 3.0},
    4:  {"material_type": "CS GALV",           "description": "CS GALV-1.5mm CA",                      "ca_mm": 1.5},
    5:  {"material_type": "CS GALV",           "description": "CS GALV-6mm CA",                        "ca_mm": 6.0},
    6:  {"material_type": "CS IC",             "description": "Carbon Steel Internally Coated",        "ca_mm": 0},
    9:  {"material_type": "SS316",             "description": "Stainless Steel 316",                   "ca_mm": 0},
    10: {"material_type": "SS316L",            "description": "Stainless Steel 316L Low Carbon",       "ca_mm": 0},
    20: {"material_type": "DSS",               "description": "Duplex Stainless Steel",                "ca_mm": 0},
    25: {"material_type": "SDSS",              "description": "Super Duplex Stainless Steel",          "ca_mm": 0},
    30: {"material_type": "CuNi",              "description": "90/10 Copper Nickel",                   "ca_mm": 0},
    31: {"material_type": "Cu",                "description": "Copper",                                "ca_mm": 0},
    40: {"material_type": "GRE",               "description": "Glass Reinforced Epoxy",                "ca_mm": 0},
    41: {"material_type": "GRV",               "description": "Glass Reinforced Vinyl Ester (BONSTRAND Series 5000C)", "ca_mm": 0},
    42: {"material_type": "CPVC",              "description": "Chlorinated Polyvinyl Chloride",        "ca_mm": 0},
    50: {"material_type": "SS316L/316 Tubing", "description": "Stainless Steel 316L/316 Tubing",      "ca_mm": 0},
    60: {"material_type": "6Mo Tubing",        "description": "6 Molybdenum Tubing",                   "ca_mm": 0},
}

PMS_TUBING_CODES = {50, 60}
PMS_NON_METALLIC_CODES = {40, 41, 42}

# ============================================================
# PMS CODE PART 3 - Optional Identifier Codes
# ============================================================
PMS_PART3_TUBING = {
    "A": {"description": "125 Barg", "pressure_barg": 125},
    "B": {"description": "200 Barg", "pressure_barg": 200},
    "C": {"description": "325 Barg", "pressure_barg": 325},
}

PMS_PART3_NON_TUBING = {
    "N": {"description": "NACE MR0175"},
    "L": {"description": "Low Temperature Service"},
}

# ============================================================
# AUTO-MAPPING: Existing material grades to PMS Part 2 codes
# ============================================================
PMS_GRADE_TO_PART2 = {
    ("A106 Gr.B", 3.0): 1,  ("A106 Gr.B", 6.0): 2,
    ("A53 Gr.B",  3.0): 1,  ("A53 Gr.B",  6.0): 2,
    ("A333 Gr.6", 3.0): 1,  ("A333 Gr.6", 6.0): 2,
    ("A312 TP316", 0.0): 9, ("A312 TP316", 0): 9,
}

PMS_LOW_TEMP_GRADES = {"A333 Gr.6"}

# ============================================================
# PMS Material Type → Default ASTM Grade Mapping
# Used when Material Type dropdown replaces individual grade cards
# ============================================================
PMS_MATERIAL_TYPE_TO_GRADE = {
    "CS":                 {"grade": "A106 Gr.B",  "base_type": "CS",    "spec": "ASTM A106", "smts": 60000, "smys": 35000, "display_name": "Carbon Steel",                "is_low_temp": False, "is_nace": False},
    "CS GALV":            {"grade": "A106 Gr.B",  "base_type": "CS",    "spec": "ASTM A106", "smts": 60000, "smys": 35000, "display_name": "Galvanised Carbon Steel",      "is_low_temp": False, "is_nace": False},
    "CS IC":              {"grade": "A106 Gr.B",  "base_type": "CS",    "spec": "ASTM A106", "smts": 60000, "smys": 35000, "display_name": "CS Internally Coated",          "is_low_temp": False, "is_nace": False},
    "SS316":              {"grade": "A312 TP316", "base_type": "SS",    "spec": "ASTM A312", "smts": 75000, "smys": 30000, "display_name": "Stainless Steel 316",           "is_low_temp": True,  "is_nace": False},
    "SS316L":             {"grade": "A312 TP316", "base_type": "SS",    "spec": "ASTM A312", "smts": 75000, "smys": 30000, "display_name": "Stainless Steel 316L",          "is_low_temp": True,  "is_nace": True},
    "DSS":                {"grade": "A312 TP316", "base_type": "SS",    "spec": "ASTM A312", "smts": 75000, "smys": 30000, "display_name": "Duplex Stainless Steel",        "is_low_temp": True,  "is_nace": True},
    "SDSS":               {"grade": "A312 TP316", "base_type": "SS",    "spec": "ASTM A312", "smts": 75000, "smys": 30000, "display_name": "Super Duplex Stainless Steel",  "is_low_temp": True,  "is_nace": True},
    "CuNi":               {"grade": "A312 TP316", "base_type": "SS",    "spec": "ASTM B466",  "smts": 50000, "smys": 18000, "display_name": "90/10 Copper Nickel",          "is_low_temp": True,  "is_nace": True},
    "Cu":                 {"grade": "A312 TP316", "base_type": "SS",    "spec": "ASTM B42",   "smts": 36000, "smys": 30000, "display_name": "Copper",                       "is_low_temp": True,  "is_nace": False},
    "GRE":                {"grade": None,          "base_type": "Non-Metallic", "spec": "ASTM D2310", "smts": None, "smys": None, "display_name": "Glass Reinforced Epoxy",  "is_low_temp": False, "is_nace": False},
    "GRV":                {"grade": None,          "base_type": "Non-Metallic", "spec": "ASTM D2310", "smts": None, "smys": None, "display_name": "GRV (BONSTRAND 5000C)",   "is_low_temp": False, "is_nace": False},
    "CPVC":               {"grade": None,          "base_type": "Non-Metallic", "spec": "ASTM F441",  "smts": None, "smys": None, "display_name": "Chlorinated PVC",         "is_low_temp": False, "is_nace": False},
    "SS316L/316 Tubing":  {"grade": "A312 TP316", "base_type": "SS",    "spec": "ASTM A269", "smts": 75000, "smys": 30000, "display_name": "SS316L/316 Tubing",             "is_low_temp": True,  "is_nace": True},
    "6Mo Tubing":         {"grade": "A312 TP316", "base_type": "SS",    "spec": "ASTM B677", "smts": 80000, "smys": 35000, "display_name": "6Mo Tubing",                    "is_low_temp": True,  "is_nace": True},
}


# ============================================================
# BRANCH CONNECTION TABLES — per API RP 14E / Company Standard
# ============================================================
# Each chart maps (run_nps, branch_nps) → connection type.
# Encoded as T-cutoff: branch >= cutoff → Tee family, else → Olet family.
# For charts with 3 zones, an additional "small_max" defines the small-branch zone.

# Material → Chart mapping
BRANCH_CHART_MAP = {
    # Chart 1
    "CS":   1, "LTCS": 1, "SS":   1, "DSS":  1, "SDSS": 1,
    # Chart 2
    "CS_GALV": 2,
    # Chart 3
    "CuNi": 3,
    # Chart 4
    "GRE":  4,
}

# ── Chart 1: CS, LTCS, SS, DSS, SDSS ──────────────────────
# Legend: W = Weldolet, T = Tee
_CHART1_RUN_SIZES    = [1, 1.5, 2, 3, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 30, 32]
_CHART1_BRANCH_SIZES = [1, 1.5, 2, 3, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 30, 32]
_CHART1_T_CUTOFF = {
    1: 1, 1.5: 1, 2: 1.5, 3: 2, 4: 2, 6: 3, 8: 4, 10: 6, 12: 8,
    14: 10, 16: 10, 18: 10, 20: 12, 22: 12, 24: 14, 30: 18, 32: 18,
}

def _chart1_lookup(run, branch):
    if branch > run:
        return None
    cutoff = _CHART1_T_CUTOFF.get(run)
    if cutoff is None:
        return None
    return "T" if branch >= cutoff else "W"

# ── Chart 2: CS GALV ──────────────────────────────────────
# Legend: H = Threadolet, W = Weldolet, T = Tee
_CHART2_RUN_SIZES    = [1, 1.5, 2, 3, 4, 6, 8, 10, 12, 14, 16, 18, 20, 24]
_CHART2_BRANCH_SIZES = [1, 1.5, 2, 3, 4, 6, 8, 10, 12, 14, 16, 18, 20, 24]
_CHART2_T_CUTOFF = {
    1: 1, 1.5: 1, 2: 1.5, 3: 3, 4: 3, 6: 3, 8: 4, 10: 6, 12: 6,
    14: 8, 16: 8, 18: 10, 20: 10, 24: 12,
}

def _chart2_lookup(run, branch):
    if branch > run:
        return None
    cutoff = _CHART2_T_CUTOFF.get(run)
    if cutoff is None:
        return None
    if branch >= cutoff:
        return "T"
    if branch <= 2:
        return "H"
    return "W"

# ── Chart 3: CuNi ─────────────────────────────────────────
# Legend: S = Sockolet, W = Weldolet, T = Tee BW
_CHART3_RUN_SIZES    = [1, 1.5, 2, 3, 4, 6, 8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36]
_CHART3_BRANCH_SIZES = [1, 1.5, 2, 3, 4, 6, 8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36]
_CHART3_T_CUTOFF = {
    1: 1, 1.5: 1, 2: 1.5, 3: 2, 4: 2, 6: 3, 8: 4, 10: 6, 12: 6,
    14: 8, 16: 8, 18: 10, 20: 10, 24: 12, 28: 12, 32: 16, 36: 16,
}

def _chart3_lookup(run, branch):
    if branch > run:
        return None
    cutoff = _CHART3_T_CUTOFF.get(run)
    if cutoff is None:
        return None
    if branch >= cutoff:
        return "T"
    if branch <= 1.5:
        return "S"
    return "W"

# ── Chart 4: GRE ──────────────────────────────────────────
# Legend: T = Equal Tee, RT = Reducing Tee, S = Reducing Saddle, - = N/A
_CHART4_RUN_SIZES    = [0.75, 1, 1.5, 2, 3, 4, 6, 8, 10, 12, 14, 16, 18, 20, 24]
_CHART4_BRANCH_SIZES = [1, 1.5, 2, 3, 4, 6, 8, 10, 12, 14, 16, 18, 20, 24]

def _chart4_lookup(run, branch):
    if branch > run:
        return None
    if run < 1:
        return "-"
    if branch == run:
        return "T"
    if branch <= 1:
        return "-"
    if run >= 6 and branch <= 2:
        return "S"
    return "RT"


# ── Unified Branch Chart API ──────────────────────────────
BRANCH_CHARTS = {
    1: {
        "chart_id": 1,
        "title": "Chart 1 (CS, LTCS, SS, DSS, SDSS)",
        "materials": ["CS", "LTCS", "SS", "DSS", "SDSS"],
        "legend": {"W": "Weldolet", "T": "Tee"},
        "run_sizes": _CHART1_RUN_SIZES,
        "branch_sizes": _CHART1_BRANCH_SIZES,
        "lookup": _chart1_lookup,
    },
    2: {
        "chart_id": 2,
        "title": "Chart 2 (CS GALV)",
        "materials": ["CS_GALV"],
        "legend": {"H": "Threadolet", "W": "Weldolet", "T": "Tee"},
        "run_sizes": _CHART2_RUN_SIZES,
        "branch_sizes": _CHART2_BRANCH_SIZES,
        "lookup": _chart2_lookup,
    },
    3: {
        "chart_id": 3,
        "title": "Chart 3 (CuNi)",
        "materials": ["CuNi"],
        "legend": {"S": "Sockolet", "W": "Weldolet", "T": "Tee BW"},
        "run_sizes": _CHART3_RUN_SIZES,
        "branch_sizes": _CHART3_BRANCH_SIZES,
        "lookup": _chart3_lookup,
    },
    4: {
        "chart_id": 4,
        "title": "Chart 4 (GRE)",
        "materials": ["GRE"],
        "legend": {"T": "Equal Tee", "RT": "Reducing Tee", "S": "Reducing Saddle", "-": "N/A"},
        "run_sizes": _CHART4_RUN_SIZES,
        "branch_sizes": _CHART4_BRANCH_SIZES,
        "lookup": _chart4_lookup,
    },
}


def get_branch_chart(material_type):
    """Return the applicable branch chart number for a material type."""
    return BRANCH_CHART_MAP.get(material_type, 1)  # default Chart 1


def branch_lookup(material_type, run_nps, branch_nps):
    """Look up the branch connection type for given material, run and branch NPS."""
    chart_num = get_branch_chart(material_type)
    chart = BRANCH_CHARTS.get(chart_num)
    if not chart:
        return None
    return chart["lookup"](run_nps, branch_nps)


def get_branch_table_matrix(chart_num):
    """Generate the full branch table matrix for display."""
    chart = BRANCH_CHARTS.get(chart_num)
    if not chart:
        return None
    run_sizes = chart["run_sizes"]
    branch_sizes = chart["branch_sizes"]
    lookup = chart["lookup"]
    matrix = []
    for run in run_sizes:
        row = {"run_nps": run, "cells": []}
        for branch in branch_sizes:
            val = lookup(run, branch)
            row["cells"].append(val if val else "")
        matrix.append(row)
    return {
        "chart_id": chart["chart_id"],
        "title": chart["title"],
        "legend": chart["legend"],
        "branch_sizes": branch_sizes,
        "rows": matrix,
    }
