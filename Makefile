.PHONY: test doctor deep apply ci

test:
	./scripts/etherea-doctor

doctor:
	./scripts/etherea-doctor --deep

apply:
	./scripts/etherea-doctor --apply

ci:
	./scripts/etherea-doctor
