import pytest


def test_avatar_bounces_within_bounds():
    pytest.importorskip("PySide6")
    try:
        from PySide6.QtCore import QPointF, QRectF
    except ImportError as exc:
        pytest.skip(f"QtGui unavailable: {exc}")

    try:
        from corund.ui.avatar.avatar_entity import AvatarEntity
    except ImportError as exc:
        pytest.skip(f"Avatar dependencies unavailable: {exc}")

    entity = AvatarEntity(radius=10.0)
    bounds = QRectF(0, 0, 100, 100)
    entity.setPos(95, 50)
    entity.velocity = QPointF(50, 0)

    entity.tick(0.1, bounds, None)

    assert entity.x() <= bounds.right() - entity.radius
    assert entity.velocity.x() <= 0
