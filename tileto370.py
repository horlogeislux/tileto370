#!/usr/bin/env python3
"""Convert NetHack 3.6.x tilesets to the NetHack 3.7.0 beta layout."""
# MIT License

# Copyright (c) 2025 Hector Denis

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# SPDX-License-Identifier: MIT

import argparse
import logging
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import IntEnum, unique
from pathlib import Path
from typing import Final

from PIL import Image, ImageColor

logger = logging.getLogger(__name__)

TileExtractor = Callable[[int], Image.Image | None]

OUTPUT_SUFFIX: Final[str] = "-370"
TILES_PER_ROW: Final[int] = 40
OUTPUT_TILE_ROWS: Final[int] = 58
STATUE_TILE_ID_OFFSET: Final[int] = 1082
FALLBACK_BACKGROUND_COLOR: Final[str] = "magenta"


@unique
class TileAlias(IntEnum):
    """Redirections for 3.7 tiles that have no exact 3.6 tile."""

    DisplacerBeast = -38  # displacer beast -> panther
    GoldBabyDragon = -143  # gold baby dragon -> yellow baby dragon
    GoldDragon = -153  # gold dragon -> yellow dragon
    GeneticEngineer = -212  # genetic engineer -> quantum mechanic
    GenericStrange = -394  # generic strange ] -> strange object
    GenericWeapon = -411  # generic weapon ) -> dagger
    GenericArmor = -509  # generic armor [ -> leather armor
    GenericRing = -546  # generic ring o -> wooden ring
    GenericAmulet = -575  # generic amulet " -> spherical amulet
    GenericTool = -592  # generic tool ( -> skeleton key
    GenericFood = -664  # generic food % -> food ration
    GenericPotion = -668  # generic potion ! -> ruby potion
    GenericScroll = -694  # generic scroll ? -> scroll of enchant armor
    GenericSpellbook = -737  # generic spellbook + -> parchment spellbook
    GenericWand = -780  # generic wand / and wand of statis -> glass wand
    GenericCoin = -807  # generic coin $ -> gold piece
    GenericGem = -808  # generic gem * -> white gem
    GenericLargeRock = -844  # generic large rock ` -> boulder
    GenericIronBall = -846  # generic iron ball 0 -> heavy iron ball
    GenericIronChain = -847  # generic iron chain _ -> iron chain
    GenericVenom = -849  # generic venom . -> splash of acid venom
    SilverMace = -450  # silver mace -> mace
    WoodenShield = -525  # shields of drain/shock resistance -> small shield
    CrystalHelmet = -471  # crystal helmet / helm of brilliance -> dented pot
    GoldDragonScaleMail = -485  # gold dragon scale mail -> yellow dragon scale mail
    GoldDragonScales = -495  # gold dragon scales -> yellow dragon scales
    PerforatedAmulet = -578  # perforated amulet -> pyramidal amulet
    CubicalAmulet = -574  # cubical amulet -> circular amulet (heart-shaped)
    CheckeredSpellbook = -741  # checkered spellbook -> mottled
    EngravingInRoom = -869  # engraving in a room -> floor of a room
    EngravingInCorridor = -872  # engraving in a corridor -> lit corridor
    BranchStaircaseUp = -873  # branch staircase up -> staircase up
    BranchStaircaseDown = -874  # branch staircase down -> staircase down
    BranchLadderUp = -875  # branch ladder up -> ladder up
    BranchLadderDown = -876  # branch ladder down -> ladder down
    Altar = -877  # * altar -> altar
    WallOfLava = -884  # wall of lava -> molten lava
    TrappedDoor = -866  # trapped door -> horizontal closed door

    # Statue redirections
    DisplacerBeastStatue = DisplacerBeast - STATUE_TILE_ID_OFFSET
    GoldBabyDragonStatue = GoldBabyDragon - STATUE_TILE_ID_OFFSET
    GoldDragonStatue = GoldDragon - STATUE_TILE_ID_OFFSET
    GeneticEngineerStatue = GeneticEngineer - STATUE_TILE_ID_OFFSET


def duplicate_values(values: Sequence[int]) -> list[int]:
    """Return [a, b, c] as [a, a, b, b, c, c]."""
    duplicated: list[int] = []
    for value in values:
        duplicated.append(value)
        duplicated.append(value)
    return duplicated


def duplicate_range(start: int, stop: int) -> list[int]:
    """Duplicate each value in range(start, stop)."""
    return duplicate_values(range(start, stop))


def index_range(start: int, stop: int) -> list[int]:
    """Return a plain list(range(start, stop))."""
    return list(range(start, stop))


def build_tile_order() -> tuple[int, ...]:
    """Build the 3.7 tile output order mapped to 3.6 tile indices."""
    return (
        *duplicate_range(0, 41),
        *[TileAlias.DisplacerBeast] * 2,
        *duplicate_range(41, 135),
        *[TileAlias.GoldBabyDragon] * 2,
        *duplicate_range(135, 145),
        *[TileAlias.GoldDragon] * 2,
        *duplicate_range(145, 213),
        *[TileAlias.GeneticEngineer] * 2,
        *duplicate_range(213, 293),
        # succubus and incubus merge as male/female versions
        295,
        293,
        # horned devil (294) that was between goes after
        294,
        294,
        *duplicate_range(296, 337),
        # caveman/woman
        337,
        338,
        *duplicate_range(339, 342),
        # priest/priestess
        342,
        343,
        *duplicate_range(344, 393),
        393,  # invisible monster
        394,  # strange object
        TileAlias.GenericStrange,
        TileAlias.GenericWeapon,
        TileAlias.GenericArmor,
        TileAlias.GenericRing,
        TileAlias.GenericAmulet,
        TileAlias.GenericTool,
        TileAlias.GenericFood,
        TileAlias.GenericPotion,
        TileAlias.GenericScroll,
        TileAlias.GenericSpellbook,
        TileAlias.GenericWand,
        TileAlias.GenericCoin,
        TileAlias.GenericGem,
        TileAlias.GenericLargeRock,
        TileAlias.GenericIronBall,
        TileAlias.GenericIronChain,
        TileAlias.GenericVenom,
        *index_range(395, 451),
        TileAlias.SilverMace,
        *index_range(451, 472),
        TileAlias.CrystalHelmet,
        *index_range(472, 477),
        TileAlias.GoldDragonScaleMail,
        *index_range(477, 487),
        TileAlias.GoldDragonScales,
        *index_range(487, 526),
        # shields of drain/shock resistance
        TileAlias.WoodenShield,
        TileAlias.WoodenShield,
        *index_range(526, 583),
        TileAlias.PerforatedAmulet,
        TileAlias.CubicalAmulet,
        *index_range(583, 777),
        TileAlias.CheckeredSpellbook,
        *index_range(777, 785),
        # wand of stasis -> glass wand
        TileAlias.GenericWand,
        *index_range(785, 871),
        TileAlias.EngravingInRoom,
        871,
        872,
        TileAlias.EngravingInCorridor,
        873,
        874,
        875,
        876,
        TileAlias.BranchStaircaseUp,
        TileAlias.BranchStaircaseDown,
        TileAlias.BranchLadderUp,
        TileAlias.BranchLadderDown,
        # unaligned/chaotic/neutral/lawful altar
        *[TileAlias.Altar] * 4,
        *index_range(877, 885),
        TileAlias.WallOfLava,
        *index_range(885, 915),
        TileAlias.TrappedDoor,
        TileAlias.GenericStrange,
        # zaps
        *index_range(1000, 1032),
        *index_range(919, 1000),
        *index_range(1032, 1038),
        850,  # unexplored
        850,  # nothing
        *index_range(1038, 1082),
        *duplicate_range(1082, 1123),
        *[TileAlias.DisplacerBeastStatue] * 2,
        *duplicate_range(1123, 1217),
        *[TileAlias.GoldBabyDragonStatue] * 2,
        *duplicate_range(1217, 1227),
        *[TileAlias.GoldDragonStatue] * 2,
        *duplicate_range(1227, 1295),
        *[TileAlias.GeneticEngineerStatue] * 2,
        *duplicate_range(1295, 1375),
        # succubus, incubus, horned devil
        1377,
        1375,
        1376,
        1376,
        *duplicate_range(1378, 1419),
        # caveman/woman
        1419,
        1420,
        *duplicate_range(1421, 1424),
        # priest/priestess
        1424,
        1425,
        *duplicate_range(1426, 1475),
        1475,
        *[1476] * 20,
    )


TILE_ORDER: Final[tuple[int, ...]] = build_tile_order()


class ConversionModeError(ValueError):
    """Raised when mode selection cannot be interpreted."""


class FuseModeSizeError(ValueError):
    """Raised when fuse background dimensions do not match expected output size."""


@dataclass(frozen=True, slots=True)
class ConversionOptions:
    """Options shared across conversions."""

    tile_width: int
    tile_height: int
    mode: str = FALLBACK_BACKGROUND_COLOR
    suffix: str = OUTPUT_SUFFIX

    @property
    def output_size(self) -> tuple[int, int]:
        """Output image size in pixels."""
        return (TILES_PER_ROW * self.tile_width, OUTPUT_TILE_ROWS * self.tile_height)


class TilesetConverter:
    """Convert one NetHack 3.6.x tileset image to 3.7.0 layout."""

    def __init__(self, source_path: Path, options: ConversionOptions) -> None:
        """Open the source tileset and initialize output/extraction strategy."""
        self._source_image: Image.Image = Image.open(source_path)
        self._options = options
        self._output_image: Image.Image = self._create_output_canvas(options.mode)
        self._tile_extractor: TileExtractor = self._select_extractor(options.mode)

    @staticmethod
    def is_pillow_color(candidate: str) -> bool:
        """Return True if PIL can parse the color."""
        try:
            ImageColor.getrgb(candidate)
        except ValueError:
            return False
        return True

    def _create_output_canvas(self, mode: str) -> Image.Image:
        """Create the output image according to mode."""
        background = mode if self.is_pillow_color(mode) else FALLBACK_BACKGROUND_COLOR
        default_canvas = Image.new("RGB", self._options.output_size, color=background)

        mode_path = Path(mode)
        if not mode_path.is_file():
            return default_canvas

        with Image.open(mode_path) as fused_canvas:
            if fused_canvas.size != self._options.output_size:
                msg = (
                    f"error in fuse mode: {mode} has size {fused_canvas.size} "
                    f"expected {self._options.output_size}"
                )
                raise FuseModeSizeError(msg)
            return fused_canvas.copy()

    def _select_extractor(self, mode: str) -> TileExtractor:
        """Resolve tile extraction strategy from mode."""
        if mode == "redirect":
            return lambda tile_id: self.extract_tile(tile_id, redirect_negative=True)

        if mode == "chess":
            raise NotImplementedError

        mode_path = Path(mode)
        if self.is_pillow_color(mode) or mode_path.is_file():
            # Keep negatives empty so background remains visible.
            return self.extract_tile

        if mode_path.is_dir():
            raise NotImplementedError

        raise ConversionModeError(mode)

    def extract_tile(
        self,
        tile_id: int,
        *,
        redirect_negative: bool = False,
    ) -> Image.Image | None:
        """Extract a source tile from its linear tile id."""
        if tile_id < 0:
            if not redirect_negative:
                return None
            tile_id = -tile_id

        source_row, source_column = divmod(tile_id, TILES_PER_ROW)
        left = source_column * self._options.tile_width
        top = source_row * self._options.tile_height

        return self._source_image.crop(
            (
                left,
                top,
                left + self._options.tile_width,
                top + self._options.tile_height,
            ),
        )

    def convert(self) -> None:
        """Populate output image according to TILE_ORDER."""
        for output_index, source_tile_id in enumerate(TILE_ORDER):
            tile = self._tile_extractor(source_tile_id)
            if tile is None:
                continue

            output_row, output_column = divmod(output_index, TILES_PER_ROW)
            self._output_image.paste(
                tile,
                (
                    output_column * self._options.tile_width,
                    output_row * self._options.tile_height,
                ),
            )

    def save_with_suffix(self, destination_path: Path) -> None:
        """Save conversion output next to destination_path using configured suffix."""
        output_path = destination_path.with_stem(
            destination_path.stem + self._options.suffix,
        )
        self._output_image.save(output_path)

    def close(self) -> None:
        """Release opened source and output images."""
        self._source_image.close()
        self._output_image.close()


def configure_logging() -> None:
    """Configure file and stdout logging."""
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(filename="converter.log"),
            logging.StreamHandler(stream=sys.stdout),
        ],
    )
    logging.getLogger("PIL").setLevel(logging.WARNING)


def make_parser() -> argparse.ArgumentParser:
    """Create the CLI parser."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.HelpFormatter,
        prog="horlogeislux's tileset converter",
        description="Convert NetHack 3.6.x tileset(s) to NetHack 3.7.0 beta format.",
        epilog="",
        add_help=False,
    )

    # Manually re-add help with --help, to keep -h available.
    parser.add_argument(
        "--help",
        action="help",
        help="Show this help message and exit.",
    )

    # One (or more) images that must share tile width and height.
    parser.add_argument(
        "paths",
        type=Path,
        nargs="+",
        help="Path(s) to the tileset(s) image(s) in NetHack 3.6.x format.",
    )

    parser.add_argument(
        "--tile-width",
        "-w",
        type=int,
        help=(
            "Width of a single tile in pixels. "
            "If only one of width/height is provided, it will be used for both."
        ),
    )

    parser.add_argument(
        "--tile-height",
        "-h",
        type=int,
        help=(
            "Height of a single tile in pixels."
            "If only one of width/height is provided, it will be used for both."
        ),
    )

    parser.add_argument(
        "--suffix",
        type=str,
        default=OUTPUT_SUFFIX,
        help="The conversion of image.ext will output imageSUFFIX.ext",
    )

    parser.add_argument(
        "--mode",
        "-m",
        default=FALLBACK_BACKGROUND_COLOR,
        help="Mode selection. By default, the background color is magenta.",
    )

    return parser


def resolve_tile_dimensions(
    parser: argparse.ArgumentParser,
    tile_width: int | None,
    tile_height: int | None,
) -> tuple[int, int]:
    """Apply implicit square behavior for tile dimensions."""
    if tile_width is None:
        if tile_height is None:
            message = "At least one of --tile-width or --tile-height must be specified."
            logger.critical(message)
            parser.error(message)

        return tile_height, tile_height

    if tile_height is None:
        return tile_width, tile_width

    return tile_width, tile_height


def convert_file(source_path: Path, options: ConversionOptions) -> None:
    """Convert one file and save it with the configured suffix."""
    converter = TilesetConverter(source_path, options)
    try:
        converter.convert()
        converter.save_with_suffix(source_path)
    finally:
        converter.close()


def run(
    paths: list[Path],
    tile_width: int,
    tile_height: int,
    mode: str,
    suffix: str,
) -> None:
    """Loop over all tilesets and convert them to the new format."""
    options = ConversionOptions(
        tile_width=tile_width,
        tile_height=tile_height,
        mode=mode,
        suffix=suffix,
    )

    for path in paths:
        if not path.is_file():
            logger.warning(
                "warning: %s is not a file: check the path. (continuing)",
                path,
            )
            continue

        convert_file(path, options)


def parse_cli_args(
    parser: argparse.ArgumentParser,
) -> tuple[list[Path], int, int, str, str]:
    """Parse CLI arguments and return normalized values."""
    args = parser.parse_args()
    tile_width, tile_height = resolve_tile_dimensions(
        parser,
        args.tile_width,
        args.tile_height,
    )
    return args.paths, tile_width, tile_height, args.mode, args.suffix


def main() -> None:
    """CLI entry point."""
    configure_logging()
    parser = make_parser()

    paths, tile_width, tile_height, mode, suffix = parse_cli_args(parser)

    try:
        run(paths, tile_width, tile_height, mode, suffix)
    except ConversionModeError:
        logger.critical(
            "error for mode: please enter a valid mode or color: got %s",
            mode,
        )
        logger.critical("wanted: PIL color, or folder of images, or sparse tileset")
        raise SystemExit(1) from None
    except FuseModeSizeError as exc:
        logger.critical(str(exc))
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
