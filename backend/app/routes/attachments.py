import os
import mimetypes
from flask import Blueprint, request, jsonify, send_file, abort
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from app.extensions import db
from app.models import MessageAttachment, Message, Conversation, User
from app.services.storage_service import StorageService

attachments_bp = Blueprint('attachments', __name__, url_prefix='/api/attachments')


@attachments_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_attachment():
    """
    Upload an attachment file.
    Optionally associates with a conversation_id and/or message_id.
    If message_id is provided, creates a MessageAttachment database record immediately.
    Otherwise, returns stored metadata so the message composer can link it on send.
    """
    if 'file' not in request.files:
        return jsonify({"success": False, "error": {"code": "NO_FILE", "message": "لم يتم العثور على أي ملف للرفع."}}), 400

    file = request.files['file']
    if not file or not file.filename:
        return jsonify({"success": False, "error": {"code": "EMPTY_FILENAME", "message": "اسم الملف غير صالح."}}), 400

    conv_id = request.form.get('conversation_id')
    msg_id = request.form.get('message_id')
    direction = request.form.get('direction', 'outbound')

    try:
        saved_info = StorageService.save_file(file)
    except ValueError as e:
        return jsonify({"success": False, "error": {"code": "VALIDATION_ERROR", "message": str(e)}}), 400
    except Exception as e:
        return jsonify({"success": False, "error": {"code": "STORAGE_ERROR", "message": f"فشل حفظ الملف: {str(e)}"}}), 500

    attachment_record = None
    if msg_id:
        try:
            msg = Message.query.get(int(msg_id))
            if msg:
                attachment_record = MessageAttachment(
                    message_id=msg.id,
                    conversation_id=msg.conversation_id,
                    file_type=saved_info['file_type'],
                    file_url=saved_info['file_url'],
                    file_name=saved_info['file_name'],
                    file_size=saved_info['file_size'],
                    storage_key=saved_info['storage_key'],
                    mime_type=saved_info['mime_type'],
                    direction=direction,
                    status='completed'
                )
                db.session.add(attachment_record)
                db.session.commit()
                saved_info['id'] = attachment_record.id
        except Exception as e:
            db.session.rollback()

    return jsonify({
        "success": True,
        "attachment": saved_info
    }), 201


@attachments_bp.route('/<int:att_id>', methods=['GET'])
@jwt_required()
def get_attachment_metadata(att_id):
    """Retrieve metadata for a specific message attachment."""
    attachment = MessageAttachment.query.get(att_id)
    if not attachment:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "المرفق غير موجود."}}), 404

    return jsonify({
        "success": True,
        "attachment": attachment.to_dict()
    }), 200


@attachments_bp.route('/<int:att_id>/download', methods=['GET'])
def download_attachment_by_id(att_id):
    """Download an attachment file by attachment ID."""
    attachment = MessageAttachment.query.get(att_id)
    if not attachment:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "المرفق غير موجود."}}), 404

    file_path = StorageService.get_file_path(attachment.storage_key)
    if not file_path:
        return jsonify({"success": False, "error": {"code": "FILE_NOT_FOUND", "message": "الملف الفعلي غير متوفر على وحدة التخزين."}}), 404

    mime = attachment.mime_type
    if not mime:
        mime, _ = mimetypes.guess_type(file_path)

    res = send_file(
        file_path,
        as_attachment=True,
        download_name=attachment.file_name or os.path.basename(file_path),
        mimetype=mime or 'application/octet-stream'
    )
    res.headers['Access-Control-Allow-Origin'] = '*'
    return res


@attachments_bp.route('/<int:att_id>/preview', methods=['GET'])
def preview_attachment_by_id(att_id):
    """Inline view/preview of an attachment by ID."""
    attachment = MessageAttachment.query.get(att_id)
    if not attachment:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "المرفق غير موجود."}}), 404

    file_path = StorageService.get_file_path(attachment.storage_key)
    if not file_path:
        return jsonify({"success": False, "error": {"code": "FILE_NOT_FOUND", "message": "الملف الفعلي غير متوفر على وحدة التخزين."}}), 404

    mime = attachment.mime_type
    if not mime:
        mime, _ = mimetypes.guess_type(file_path)

    res = send_file(
        file_path,
        as_attachment=False,
        mimetype=mime or 'application/octet-stream'
    )
    res.headers['Cache-Control'] = 'public, max-age=86400'
    res.headers['Access-Control-Allow-Origin'] = '*'
    return res


@attachments_bp.route('/preview/<storage_key>', methods=['GET'])
def preview_by_storage_key(storage_key):
    """Inline stream / preview by storage key."""
    file_path = StorageService.get_file_path(storage_key)
    if not file_path:
        abort(404)

    # Lookup attachment record if exists for proper mime type & name
    att = MessageAttachment.query.filter_by(storage_key=storage_key).first()
    mime = att.mime_type if att and att.mime_type else None
    if not mime:
        mime, _ = mimetypes.guess_type(file_path)

    res = send_file(
        file_path,
        as_attachment=False,
        mimetype=mime or 'application/octet-stream'
    )
    res.headers['Cache-Control'] = 'public, max-age=86400'
    res.headers['Access-Control-Allow-Origin'] = '*'
    return res


@attachments_bp.route('/download/<storage_key>', methods=['GET'])
def download_by_storage_key(storage_key):
    """Download file by storage key."""
    file_path = StorageService.get_file_path(storage_key)
    if not file_path:
        abort(404)

    att = MessageAttachment.query.filter_by(storage_key=storage_key).first()
    filename = (att.file_name if att and att.file_name else None) or os.path.basename(file_path)
    mime = (att.mime_type if att and att.mime_type else None)
    if not mime:
        mime, _ = mimetypes.guess_type(file_path)

    res = send_file(
        file_path,
        as_attachment=True,
        download_name=filename,
        mimetype=mime or 'application/octet-stream'
    )
    res.headers['Access-Control-Allow-Origin'] = '*'
    return res


