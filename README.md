# Circle Drawer 🎨

Draw perfect circles on [Neal.fun Perfect Circle Challenge](https://neal.fun/perfect-circle/) automatically.

## Installation

```bash
pip install pynput
```

## How to Use

1. Run the script:
   ```bash
   python circle_drawer.py
   ```

2. Go to [https://neal.fun/perfect-circle/](https://neal.fun/perfect-circle/)

3. Position your mouse at the **center** of the dot

4. Press **Left Alt** to start drawing

5. Watch the perfect circle appear

6. Press **ESC** to exit anytime

## Change Configuration

### Option 1: Edit config.json

Open `config.json` and change the values:

```json
{
  "radius": 340,
  "steps": 2000,
  "draw_speed": 0.002,
  "start_key": "alt_l",
  "exit_key": "esc"
}
```

**Settings:**
- `radius` - Size of circle in pixels (default: 340)
- `steps` - Smoothness level (default: 2000)
- `draw_speed` - Speed in seconds (0 = fastest, default: 0.002)
- `start_key` - Key to start (alt_l, alt_r, ctrl_l, ctrl_r, shift_l, shift_r, space, enter)
- `exit_key` - Key to stop (esc, escape, q, space)

### Option 2: Use GUI Tool

```bash
python circle_drawer.py config
```

Opens a window with sliders to adjust settings easily.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Circle not drawing | Make sure the game page is focused and cursor is at exact center |
| Wrong size | Adjust `radius` in config.json |
| Too fast/slow | Change `draw_speed` in config.json |
| Can't exit | Press ESC (or your exit key) |
