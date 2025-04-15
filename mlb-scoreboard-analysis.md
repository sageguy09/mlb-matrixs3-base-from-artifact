# Atlanta Braves LED Matrix Scoreboard: Full Project Analysis

## Project Overview

This project aims to create a dynamic 64x32 RGB LED Matrix scoreboard for Atlanta Braves baseball games using an Adafruit MatrixPortal S3 running CircuitPython. The scoreboard will display different visual layouts depending on whether the Braves are currently playing and will fetch live game data from ESPN's API.

## Display Modes

Based on the provided requirements, the project needs two primary display modes:

### 1. Game Day Mode
When the Braves are playing, the display should show:
- Braves logo (persistently visible)
- Current opponent (team abbreviation)
- Inning status (top/bottom and number)
- Base occupation visualization
- Ball-Strike-Out counts
- Current score

### 2. Off Day Mode
When no game is scheduled, the display should show:
- Larger or centered Braves logo
- Team's current win-loss record
- Next game information (date, time, opponent)

## Hardware Analysis

The system is built on:
- **Adafruit MatrixPortal S3**: An all-in-one ESP32-S3 based controller
- **64x32 HUB75 RGB LED Matrix**: Providing a 64×32 pixel display area
- **WiFi Connectivity**: For fetching live game data

## Reference Project Insights

The MLB-LED-Scoreboard GitHub project offers several valuable implementation approaches:

1. **Configuration-Based Layout System**: Uses JSON configuration files (`/data/scoreboard/w64h32.json`, `w128h32.json`, etc.) to define pixel-precise positioning of all display elements for different screen sizes
2. **Base Runner Visualization**: Uses a diamond-shaped pixel layout rather than Unicode characters
3. **Layout Optimization**: Employs different layouts depending on game state
4. **API Integration**: Uses ESPN/MLB APIs to fetch live game data
5. **Memory Management**: Implements efficient resource usage for constrained environments

The Adafruit Sports Scoreboard guide provides additional insights on:
1. **Memory-efficient display techniques** for CircuitPython
2. **Effective information hierarchy** for small displays
3. **Color selection guidelines** for LED matrix readability

## Implementation Strategy

### Display Layout Design

#### Game Day Layout (64×32 pixels)
```
+----------------------------------------------------------------+
|                                                                |
| [LOGO]  ATL v XXX      ┌───┐                                  |
| (16x16) T/B Inn        │   │         B:# S:# O:#              |
|         SCORE: #-#     └───┘                                  |
|                                                                |
+----------------------------------------------------------------+
```

#### Off Day Layout (64×32 pixels)
```
+----------------------------------------------------------------+
|                                                                |
|                    +-----------+                               |
|                    |   BRAVES  |                               |
|                    |    LOGO   |                               |
|                    +-----------+                               |
|                                                                |
|                    RECORD: ##-##                               |
|                                                                |
|                NEXT: MM/DD vs XXX H:MM                         |
|                                                                |
+----------------------------------------------------------------+
```

### Technical Components

#### 1. Display Management
- **DisplayIO Groups**: Using layered groups for organized screen elements
- **Memory Optimization**: Proper cleanup and resource management
- **Bitmap Handling**: Efficient logo display and scaling

#### 2. Base Visualization
After studying the reference implementation, a custom pixel-based diamond is recommended over Unicode characters:
```
       [2]        
      /   \       
     /     \      
[3] ------- [1] 
     \     /      
      \   /       
       [H]        
```

#### 3. ESPN API Integration
The implementation will fetch data from ESPN's site API:
- `https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/15/schedule` (Braves team ID = 15)
- Data will include game status, score, inning, count, and base runners

#### 4. Update Logic
- During active games: Update every 30-60 seconds
- During off days: Update every few hours
- Error handling for network issues with graceful fallback

## Implementation Code Structure

The core components of the implementation will include:

1. **Display Initialization**
   - Proper matrix setup
   - DisplayIO group management
   - Logo bitmap loading

2. **Configuration-Based Layout System**
   - JSON/TOML layout configuration file (`/layouts/w64h32.json`)
   - Coordinates for all display elements (x, y positions)
   - Color and font settings
   - Position parsing and application

3. **Layout Managers**
   - Game day layout function
   - Off day layout function
   - Base runner visualization generator

4. **Data Fetching**
   - ESPN API integration
   - JSON parsing
   - Error handling

5. **Main Loop**
   - State management
   - Update scheduling
   - Memory optimization

## Memory Considerations

The MatrixPortal S3's ESP32-S3 has limited RAM, requiring careful resource management:

1. Use `gc.collect()` strategically after display updates
2. Minimize string operations in critical paths
3. Reuse DisplayIO groups when possible
4. Limit the number of labels and graphical elements
5. Implement progressive updates (refresh only what changes)

## Design Challenges and Solutions

1. **Challenge**: Limited 64×32 pixel resolution
   **Solution**: Configuration-based layout system with pixel-level precision

2. **Challenge**: Memory constraints on microcontroller
   **Solution**: Strategic garbage collection and resource reuse

3. **Challenge**: API reliability and rate limits
   **Solution**: Caching, error handling, and appropriate update intervals

4. **Challenge**: Font legibility on matrix display
   **Solution**: Custom bitmap font or careful font selection for readability

5. **Challenge**: Layout flexibility for different screen sizes
   **Solution**: Create swappable JSON layout configurations for each resolution

6. **Challenge**: Hard-to-maintain hardcoded coordinates
   **Solution**: Move all positioning to configuration files

## Future Enhancement Opportunities

1. **Animation Effects**: Run scored celebrations, logo animations
2. **Additional Stats**: Pitcher/batter information, team standings
3. **Multi-Game Display**: Rotation of scores from other games
4. **Interactive Features**: Button controls for display modes
5. **Historical Stats**: Team record visualization
6. **Multiple Display Sizes**: Support for various matrix configurations (64x64, 128x32, etc.)
7. **Layout Editor**: Web-based tool to adjust element positions visually
8. **Multi-Team Support**: Configurable favorite team selection

## Development Steps

1. Set up basic display components
2. Implement game day layout
3. Test with simulated game data
4. Implement ESPN API integration
5. Add off day layout
6. Optimize memory usage and performance
7. Deploy and monitor for extended usage

## Next Steps

The immediate focus should be on implementing the Game Day layout with a static configuration, ensuring the base runner diamond visualization works correctly, and then integrating with the ESPN API for live data.