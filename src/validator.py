class Validator:
    @staticmethod
    def _raise(error_type, message: str):
        if error_type:
            raise error_type(message)
        raise TypeError(message)

    @staticmethod
    def validate(var, expec: str, error_type=None):
        """
        Supported expec values:
          - "dict", "list", "str", "int", "bool", "number"
          - "list[str]", "list[int]"
        """
        def type_err():
            Validator._raise(error_type, f"🛑 expected type '{expec}' got type '{type(var)}'")

        if expec == "dict":
            if not isinstance(var, dict):
                type_err()
            return

        if expec == "list":
            if not isinstance(var, list):
                type_err()
            return

        if expec == "str":
            if not isinstance(var, str):
                type_err()
            return

        if expec == "int":
            if not isinstance(var, int):
                type_err()
            return

        if expec == "bool":
            if not isinstance(var, bool):
                type_err()
            return

        if expec == "number":
            if not isinstance(var, (int, float)):
                type_err()
            return

        if expec == "list[str]":
            if not isinstance(var, list) or any(not isinstance(v, str) for v in var):
                type_err()
            return

        if expec == "list[int]":
            if not isinstance(var, list) or any(not isinstance(v, int) for v in var):
                type_err()
            return

        # Unsupported type label
        raise ValueError(f"🛑 '{expec}' is not a supported type")

    @staticmethod
    def validate_dict(
        input_dict: dict,
        keys_mandatory: list | None = None,
        keys_mandatory_types: list | None = None,
        # kept for signature compatibility; ignored in this minimal version
        keys_optional: list | None = None,
        keys_optional_types: list | None = None,
        error_type=None,
    ):
        """
        Minimal dict validator:
          - Ensures input_dict is a dict and not empty
          - If keys_mandatory is provided, ensures they exist
          - If keys_mandatory_types is provided, checks types for corresponding keys
        """
        # input_dict must be a non-empty dict
        Validator.validate(input_dict, "dict", error_type)
        if not input_dict:
            Validator._raise(error_type, "🛑 input_dict is empty")

        # If no mandatory requirements provided, nothing to do
        if not keys_mandatory and not keys_mandatory_types:
            return

        # Validate mandatory keys list if provided
        if keys_mandatory is not None:
            Validator.validate(keys_mandatory, "list", error_type)
            if not keys_mandatory:
                Validator._raise(error_type, "🛑 keys_mandatory is empty")

            # Ensure presence
            missing = [k for k in keys_mandatory if k not in input_dict]
            if missing:
                Validator._raise(
                    error_type,
                    f"🛑 mandatory key(s) missing: {missing}",
                )

        # Validate types for mandatory keys if provided
        if keys_mandatory_types is not None:
            Validator.validate(keys_mandatory_types, "list[str]", error_type)

            if keys_mandatory is None or len(keys_mandatory) != len(keys_mandatory_types):
                Validator._raise(
                    error_type,
                    "🛑 keys_mandatory and keys_mandatory_types must be same length",
                )

            for key, type_label in zip(keys_mandatory, keys_mandatory_types):
                # If a key is missing here, treat as error (should have been caught above)
                if key not in input_dict:
                    Validator._raise(
                        error_type,
                        f"🛑 mandatory key {key} not present in dictionary",
                    )
                Validator.validate(input_dict[key], type_label, error_type)