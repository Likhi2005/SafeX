"""
WebSocket service for real-time threat intelligence updates.
"""

import logging
from flask_socketio import SocketIO, emit, join_room, leave_room
from threading import Timer
from datetime import datetime, timezone
from backend.services.threat_intelligence import threat_intelligence

logger = logging.getLogger(__name__)

class ThreatWebSocketService:
    """WebSocket service for real-time threat updates."""
    
    def __init__(self):
        self.socketio = None
        self.active_rooms = set()
        self.update_timer = None
        
    def init_app(self, app):
        """Initialize WebSocket with Flask app."""
        self.socketio = SocketIO(
            app, 
            cors_allowed_origins="*", 
            async_mode='threading',
            logger=True,
            engineio_logger=False
        )
        
        # Register event handlers
        self._register_handlers()
        
        # Start periodic updates
        self._start_periodic_updates()
        
        logger.info("WebSocket service initialized")
        return self.socketio
    
    def _register_handlers(self):
        """Register WebSocket event handlers."""
        
        @self.socketio.on('connect')
        def handle_connect():
            logger.info(f"Client connected: {request.sid if 'request' in globals() else 'unknown'}")
            emit('connection_status', {
                'status': 'connected',
                'message': 'Real-time threat feed connected',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            logger.info(f"Client disconnected")
        
        @self.socketio.on('subscribe_threats')
        def handle_threat_subscription(data):
            """Subscribe to real-time threat updates."""
            room = data.get('room', 'threats')
            join_room(room)
            self.active_rooms.add(room)
            
            logger.info(f"Client subscribed to {room}")
            
            # Send initial data
            initial_data = threat_intelligence.get_real_time_threats(minutes=30)
            emit('threat_update', {
                'type': 'initial_load',
                'data': initial_data,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }, room=room)
        
        @self.socketio.on('unsubscribe_threats')
        def handle_threat_unsubscription(data):
            """Unsubscribe from threat updates."""
            room = data.get('room', 'threats')
            leave_room(room)
            self.active_rooms.discard(room)
            logger.info(f"Client unsubscribed from {room}")
        
        @self.socketio.on('request_patterns')
        def handle_pattern_request():
            """Send attack pattern analysis."""
            patterns = threat_intelligence.detect_attack_patterns(hours=6)
            emit('pattern_update', {
                'type': 'pattern_analysis',
                'data': patterns,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        
        @self.socketio.on('request_predictions')
        def handle_prediction_request():
            """Send threat predictions."""
            predictions = threat_intelligence.get_threat_predictions()
            emit('prediction_update', {
                'type': 'threat_predictions',
                'data': predictions,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
    
    def _start_periodic_updates(self):
        """Start periodic threat updates."""
        def send_updates():
            if self.active_rooms and self.socketio:
                try:
                    # Get fresh threat data
                    threat_data = threat_intelligence.get_real_time_threats(minutes=30)
                    
                    # Send to all subscribed clients
                    for room in self.active_rooms:
                        self.socketio.emit('threat_update', {
                            'type': 'periodic_update',
                            'data': threat_data,
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        }, room=room)
                    
                    logger.debug(f"Sent periodic updates to {len(self.active_rooms)} rooms")
                    
                except Exception as e:
                    logger.error(f"Failed to send periodic updates: {e}")
            
            # Schedule next update
            self.update_timer = Timer(30.0, send_updates)  # Update every 30 seconds
            self.update_timer.start()
        
        # Start the update cycle
        send_updates()
    
    def broadcast_new_threat(self, threat_data):
        """Broadcast new threat to all connected clients."""
        if self.socketio and self.active_rooms:
            self.socketio.emit('new_threat', {
                'type': 'new_threat_alert',
                'threat': threat_data,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }, room='threats')
    
    def stop_periodic_updates(self):
        """Stop periodic updates."""
        if self.update_timer:
            self.update_timer.cancel()

# Global WebSocket service instance
ws_service = ThreatWebSocketService()