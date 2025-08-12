import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { 
  ArrowLeft, 
  Save, 
  Trash2, 
  MessageSquare, 
  Phone, 
  Calendar,
  Send,
  AlertTriangle,
  Clock
} from 'lucide-react';
import { apiService, formatters } from '../api';
import toast from 'react-hot-toast';

const MessageDetails = ({ messageId, onClose, onDeleted }) => {
  const [message, setMessage] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    watch
  } = useForm();

  useEffect(() => {
    loadMessage();
  }, [messageId]);

  const loadMessage = async () => {
    try {
      setLoading(true);
      const messageData = await apiService.getScheduledMessage(messageId);
      setMessage(messageData);
      
      // Populate form with current data
      reset({
        phone: messageData.phone,
        message: messageData.message,
        send_time: formatters.toDateTimeLocal(messageData.send_time)
      });
      
    } catch (error) {
      console.error('Error loading message:', error);
      toast.error('Error cargando mensaje');
      onClose();
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = async (data) => {
    try {
      setUpdating(true);
      
      const updateData = {
        phone: formatters.formatPhone(data.phone),
        message: data.message.trim(),
        send_time: new Date(data.send_time).toISOString()
      };

      // Validar que la fecha sea en el futuro
      const sendTime = new Date(data.send_time);
      if (sendTime <= new Date()) {
        toast.error('La fecha y hora debe ser en el futuro');
        return;
      }

      const updatedMessage = await apiService.updateScheduledMessage(messageId, updateData);
      setMessage(updatedMessage);
      
      toast.success('Mensaje actualizado correctamente');
      
    } catch (error) {
      console.error('Error updating message:', error);
      const errorMessage = error.response?.data?.detail || 'Error actualizando el mensaje';
      toast.error(errorMessage);
    } finally {
      setUpdating(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('¿Estás seguro de que quieres eliminar este mensaje?')) {
      return;
    }

    try {
      await apiService.deleteScheduledMessage(messageId);
      toast.success('Mensaje eliminado correctamente');
      onDeleted();
    } catch (error) {
      console.error('Error deleting message:', error);
      toast.error('Error eliminando mensaje');
    }
  };

  // Obtener fecha mínima (ahora + 1 minuto)
  const getMinDateTime = () => {
    const now = new Date();
    now.setMinutes(now.getMinutes() + 1);
    return formatters.toDateTimeLocal(now);
  };

  // Watch para mostrar preview
  const watchedMessage = watch('message');
  const watchedPhone = watch('phone');

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="flex items-center space-x-4 mb-6">
            <div className="h-8 w-8 bg-gray-200 rounded"></div>
            <div className="h-6 bg-gray-200 rounded w-1/4"></div>
          </div>
          <div className="space-y-4">
            <div className="h-12 bg-gray-200 rounded"></div>
            <div className="h-32 bg-gray-200 rounded"></div>
            <div className="h-8 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 bg-white rounded-lg shadow-md">
      {/* Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={onClose}
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
          aria-label="Cerrar detalles"
        >
          <ArrowLeft className="h-5 w-5" />
          <span>Volver</span>
        </button>

        <button
          onClick={handleDelete}
          className="flex items-center space-x-2 text-red-600 hover:text-red-800"
          aria-label="Eliminar mensaje"
          disabled={updating}
        >
          <Trash2 className="h-5 w-5" />
          <span>Eliminar</span>
        </button>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Phone input */}
        <div>
          <label htmlFor="phone" className="block text-sm font-medium text-gray-700">
            Teléfono
          </label>
          <input
            id="phone"
            type="tel"
            {...register('phone', {
              required: 'El teléfono es obligatorio',
              pattern: {
                value: /^\+?\d{10,15}$/,
                message: 'Número de teléfono inválido',
              },
            })}
            className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:ring focus:ring-indigo-500 ${
              errors.phone ? 'border-red-500' : ''
            }`}
            disabled={updating}
          />
          {errors.phone && (
            <p className="mt-1 text-xs text-red-600">{errors.phone.message}</p>
          )}
        </div>

        {/* Message input */}
        <div>
          <label htmlFor="message" className="block text-sm font-medium text-gray-700">
            Mensaje
          </label>
          <textarea
            id="message"
            rows={4}
            {...register('message', {
              required: 'El mensaje es obligatorio',
              maxLength: { value: 1000, message: 'Máximo 1000 caracteres' },
            })}
            className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:ring focus:ring-indigo-500 ${
              errors.message ? 'border-red-500' : ''
            }`}
            disabled={updating}
          />
          {errors.message && (
            <p className="mt-1 text-xs text-red-600">{errors.message.message}</p>
          )}
        </div>

        {/* Send time input */}
        <div>
          <label htmlFor="send_time" className="block text-sm font-medium text-gray-700">
            Fecha y Hora de Envío
          </label>
          <input
            id="send_time"
            type="datetime-local"
            {...register('send_time', { required: 'La fecha y hora es obligatoria' })}
            min={getMinDateTime()}
            className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:ring focus:ring-indigo-500 ${
              errors.send_time ? 'border-red-500' : ''
            }`}
            disabled={updating}
          />
          {errors.send_time && (
            <p className="mt-1 text-xs text-red-600">{errors.send_time.message}</p>
          )}
        </div>

        {/* Buttons */}
        <div className="flex justify-end space-x-4">
          <button
            type="submit"
            disabled={updating}
            className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
          >
            <Save className="h-5 w-5 mr-2" />
            Guardar
          </button>
        </div>
      </form>

      {/* Preview */}
      <div className="pt-6 border-t border-gray-200">
        <h4 className="text-lg font-semibold text-gray-900 mb-2">Vista previa</h4>
        <div className="bg-gray-50 p-4 rounded-md">
          <p className="text-sm font-medium text-gray-700 mb-1">
            <Phone className="inline h-4 w-4 mr-1 text-gray-500" />
            {watchedPhone || <span className="text-gray-400">Sin número</span>}
          </p>
          <p className="text-gray-800 whitespace-pre-wrap">{watchedMessage || 'Sin mensaje'}</p>
          <p className="mt-2 text-xs text-gray-500">
            <Calendar className="inline h-4 w-4 mr-1" />
            Programado para: {watch('send_time') ? formatters.toDisplayDate(watch('send_time')) : 'N/A'}
          </p>
          <p className="mt-1 text-xs flex items-center space-x-1 text-gray-500">
            <Clock className="h-4 w-4" />
            <span>
              Estado: {message?.status || 'Desconocido'}
              {message?.status === 'failed' && <AlertTriangle className="inline h-4 w-4 text-red-500 ml-1" />}
            </span>
          </p>
        </div>
      </div>
    </div>
  );
};

export default MessageDetails;