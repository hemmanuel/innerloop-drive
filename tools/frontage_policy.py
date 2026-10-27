"""Houston duplex acquisition routing; widths route review, never discard a site.

Frontage is measured along a street-facing edge, not the short dimension of a
minimum rotated rectangle. Rules below describe an equal, side-by-side split.
Other configurations remain separate candidates.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class DuplexEnvelope:
    building_width: float
    building_depth: float
    left_clearance: float
    right_clearance: float
    front_reservation: float
    rear_reservation: float

    @property
    def parcel_width(self):
        return self.building_width + self.left_clearance + self.right_clearance

    @property
    def parcel_depth(self):
        return self.building_depth + self.front_reservation + self.rear_reservation

    def fits(self, width, depth):
        return width >= self.parcel_width and depth >= self.parcel_depth


def access_route(frontage_ft, area_sqft, *, corner=False, through=False,
                 usable_alley=False, subdividing=True, street_class=None,
                 measurement_tolerance=1.0):
    """Return the next layout check, not a permit/qualification decision.

    The 15,000-sq-ft exception applies to the whole property being subdivided.
    Existing legal lots need their existing access/plat evaluated separately.
    A 1-ft GIS boundary band prevents rounding from deciding a legal threshold.
    """
    if frontage_ft is None:
        return 'measure_street_frontage'
    if through:
        return 'test_opposite_street_split'
    if corner:
        return 'test_corner_split_and_side_access'
    if usable_alley:
        return 'test_alley_loaded_split'
    if not subdividing:
        return 'test_existing_lots_and_access'
    if street_class in ('MAJOR','FREEWAY','RAMP','THOROUGHFARE'):
        return 'test_thoroughfare_access'
    if min(abs(frontage_ft - n) for n in (66, 88)) <= measurement_tolerance:
        return 'measure_near_access_threshold'
    width = frontage_ft / 2
    if width >= 44:
        return 'test_two_front_lots_44_plus'
    if width >= 33 and area_sqft <= 15000:
        return 'test_two_narrow_front_lots_33_to_44'
    if width >= 33:
        return 'test_shared_access_over_15000'
    return 'test_shared_access_or_alternative_split'
