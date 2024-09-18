import json
from unittest import TestCase, mock
from quart import Response
from nwc_backend.api_handlers.create_manual_connection_handler import create_manual_connection
from nwc_backend.db import db
from nwc_backend.models.nwc_connection import NWCConnection
from nwc_backend.models.permissions_grouping import PermissionsGroup
from nwc_backend.nostr_client import nostr_client
from nwc_backend.nostr_config import NostrConfig
from nwc_backend.nostr_jwt import VaspJwt
from nwc_backend.utils import initialize_connection_data
from nwc_backend.utils import WerkzeugResponse

class CreateManualConnectionTest(TestCase):
    @mock.patch("nwc_backend.api_handlers.create_manual_connection_handler.Keys")
    @mock.patch("nwc_backend.api_handlers.create_manual_connection_handler.NWCConnection")
    @mock.patch("nwc_backend.api_handlers.create_manual_connection_handler.initialize_connection_data")
    @mock.patch("nwc_backend.api_handlers.create_manual_connection_handler.VaspJwt")
    @mock.patch("nwc_backend.api_handlers.create_manual_connection_handler.WerkzeugResponse")
    @mock.patch("nwc_backend.api_handlers.create_manual_connection_handler.request")
    def test_create_manual_connection(
        self,
        mock_request,
        mock_werkzeug_response,
        mock_vasp_jwt,
        mock_initialize_connection_data,
        mock_nwc_connection,
        mock_keys,
    ):
        # Mock session
        session = {"short_lived_vasp_token": "dummy_token"}

        # Mock request
        request_data = {"dummy_key": "dummy_value"}
        mock_request.get_json.return_value = request_data

        # Mock VaspJwt
        mock_vasp_jwt.from_jwt.return_value = mock_vasp_jwt

        # Mock keypair
        mock_keypair = mock.Mock()
        mock_keypair.public_key.return_value.to_hex.return_value = "dummy_public_key"
        mock_keypair.secret_key.return_value.to_hex.return_value = "dummy_secret_key"

        # Mock NWCConnection
        mock_nwc_connection.return_value = mock.Mock(
            id="dummy_id",
            get_nwc_connection_uri=mock.Mock(return_value="dummy_uri"),
        )

        # Mock Keys
        mock_keys.generate.return_value = mock_keypair

        # Mock WerkzeugResponse
        mock_werkzeug_response.return_value = "dummy_response"

        # Mock db
        mock_db_session = mock.Mock()
        mock_db_session.add.return_value = None
        mock_db_session.commit.return_value = None
        mock_db.session = mock_db_session

        # Mock nostr_client
        mock_nostr_send = mock.Mock()
        mock_nostr_send.return_value = SendEventOutput(
            id=EventId.from_hex(token_hex()),
            output=Output(success=["wss://relay.getalby.com/v1"], failed={}),
        )
        nostr_client.send_event = mock_nostr_send

        # Mock NostrConfig
        mock_nostr_config = mock.Mock()
        mock_nostr_config.get.return_value = "dummy_config"
        NostrConfig.get_instance = mock.Mock(return_value=mock_nostr_config)

        # Call the function
        with mock.patch.dict("nwc_backend.api_handlers.create_manual_connection_handler.session", session):
            with mock.patch("nwc_backend.api_handlers.create_manual_connection_handler.VaspJwt", mock_vasp_jwt):
                with mock.patch("nwc_backend.api_handlers.create_manual_connection_handler.request", mock_request):
                    with mock.patch("nwc_backend.api_handlers.create_manual_connection_handler.WerkzeugResponse", mock_werkzeug_response):
                        response = create_manual_connection()

        # Assertions
        self.assertEqual(response, "dummy_response")
        mock_vasp_jwt.from_jwt.assert_called_once_with("dummy_token")
        mock_keys.generate.assert_called_once()
        mock_nwc_connection.assert_called_once_with(
            id=mock.ANY,
            user_id=mock_vasp_jwt.user_id,
            granted_permissions_groups=[],
            nostr_pubkey="dummy_public_key",
        )
        mock_db_session.add.assert_called_once_with(mock_nwc_connection.return_value)
        mock_db_session.commit.assert_called_once()
        mock_initialize_connection_data.assert_called_once_with(
            mock_nwc_connection.return_value,
            request_data=request_data,
            short_lived_vasp_token="dummy_token",
        )
        mock_nwc_connection.return_value.get_nwc_connection_uri.assert_called_once_with("dummy_secret_key")
        mock_werkzeug_response.assert_called_once_with(
            json.dumps(
                {
                    "connectionId": "dummy_id",
                    "pairingUri": "dummy_uri",
                }
            )
        )