"""Compatibility command spelling for the explicit V4.1 SFX stage."""
import sys
from production import main
if __name__ == "__main__":
    sys.argv.insert(1,"sfx")
    main()
