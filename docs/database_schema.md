# 📊 Database Schema

## Player_Info
| Column     | Type      | Notes               |
|------------|-----------|---------------------|
| Player_ID  | INT (PK)  | Unique identifier   |
| Name       | VARCHAR   | Player name         |
| Team       | VARCHAR   | Current team        |
| Position   | VARCHAR   | Position played     |
| Height     | VARCHAR   | e.g., "6'2"         |
| Weight     | INT       | Player weight (lbs) |
| Age        | INT       | Player age          |

---

## Game_Conditions
| Column     | Type      | Notes                    |
|------------|-----------|--------------------------|
| Game_ID    | INT (PK)  | Unique identifier        |
| Team       | VARCHAR   | Player’s team            |
| Opponent   | VARCHAR   | Opponent team            |
| Home/Away  | BOOLEAN   | 1 = Home, 0 = Away       |
| Date       | DATE      | Game date                |
| Weather_ID | INT (FK)  | References **Weather_Data** |
| Win/Loss   | BOOLEAN   | 1 = Win, 0 = Loss        |

---

## Weather_Data
| Column      | Type      | Notes                       |
|-------------|-----------|-----------------------------|
| Weather_ID  | INT (PK)  | Unique identifier           |
| Temperature | FLOAT     | Temperature in °F/°C        |
| Condition   | VARCHAR   | e.g., Clear, Rain, Snow      |
| Wind_Speed  | FLOAT     | Wind speed (mph / km/h)     |
| Humidity    | FLOAT     | % humidity                  |

---

## Player_Stats
| Column     | Type      | Notes                          |
|------------|-----------|--------------------------------|
| Player_ID  | INT (FK)  | References **Player_Info**     |
| Game_ID    | INT (FK)  | References **Game_Conditions** |
| Stat_Type  | VARCHAR   | e.g., Points, Assists          |
| Stat_Value | FLOAT     | Value of the stat              |

---

## Injury_History
| Column     | Type      | Notes                        |
|------------|-----------|------------------------------|
| Injury_ID  | INT (PK)  | Unique identifier            |
| Player_ID  | INT (FK)  | References **Player_Info**   |
| Body_Part  | VARCHAR   | Injured body part            |
| Time_Missed| VARCHAR   | e.g., "2 weeks"              |

---

## 🔗 Relationships
- **Player_Info (1) → Player_Stats (many)**  
- **Game_Conditions (1) → Player_Stats (many)**  
- **Player_Info (1) → Injury_History (many)**  
- **Weather_Data (1) → Game_Conditions (many)**

