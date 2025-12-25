import { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import {
  ArrowLeft,
  Star,
  Phone,
  Globe,
  MapPin,
  Clock,
  Tag,
  MessageSquare,
  Plus,
  X,
  ExternalLink,
  Trash2,
  Loader2
} from 'lucide-react';
import { getBusiness, addTag, removeTag, addNote, deleteNote, deleteBusiness } from '../services/api';
import clsx from 'clsx';

function BusinessDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const [newTag, setNewTag] = useState('');
  const [newNote, setNewNote] = useState('');
  const [showAddNote, setShowAddNote] = useState(false);

  const { data: business, isLoading, error } = useQuery({
    queryKey: ['business', id],
    queryFn: () => getBusiness(id),
  });

  const addTagMutation = useMutation({
    mutationFn: (tag) => addTag(id, tag),
    onSuccess: () => {
      queryClient.invalidateQueries(['business', id]);
      setNewTag('');
      toast.success('Etiket eklendi');
    },
  });

  const removeTagMutation = useMutation({
    mutationFn: (tag) => removeTag(id, tag),
    onSuccess: () => {
      queryClient.invalidateQueries(['business', id]);
      toast.success('Etiket kaldırıldı');
    },
  });

  const addNoteMutation = useMutation({
    mutationFn: (note) => addNote(id, note),
    onSuccess: () => {
      queryClient.invalidateQueries(['business', id]);
      setNewNote('');
      setShowAddNote(false);
      toast.success('Not eklendi');
    },
  });

  const deleteNoteMutation = useMutation({
    mutationFn: (noteId) => deleteNote(id, noteId),
    onSuccess: () => {
      queryClient.invalidateQueries(['business', id]);
      toast.success('Not silindi');
    },
  });

  const deleteBusinessMutation = useMutation({
    mutationFn: () => deleteBusiness(id),
    onSuccess: () => {
      toast.success('İşletme silindi');
      navigate('/businesses');
    },
  });

  const handleAddTag = (e) => {
    e.preventDefault();
    if (newTag.trim()) {
      addTagMutation.mutate(newTag.trim());
    }
  };

  const handleAddNote = (e) => {
    e.preventDefault();
    if (newNote.trim()) {
      addNoteMutation.mutate(newNote.trim());
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
      </div>
    );
  }

  if (error || !business) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-500 mb-4">İşletme bulunamadı</p>
        <Link to="/businesses" className="text-primary-600 hover:text-primary-700">
          ← İşletmelere dön
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Back Button */}
      <Link 
        to="/businesses"
        className="inline-flex items-center gap-2 text-slate-600 hover:text-slate-800"
      >
        <ArrowLeft className="w-4 h-4" />
        İşletmelere Dön
      </Link>

      {/* Header Card */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-800 mb-2">{business.name}</h1>
            {business.category && (
              <span className="inline-block bg-primary-100 text-primary-700 px-3 py-1 rounded-full text-sm">
                {business.category}
              </span>
            )}
          </div>

          {business.rating && (
            <div className="flex items-center gap-2 bg-amber-50 px-4 py-2 rounded-lg">
              <Star className="w-6 h-6 text-amber-500 fill-current" />
              <div>
                <div className="text-xl font-bold text-amber-700">{business.rating}</div>
                <div className="text-xs text-amber-600">{business.rating_count} yorum</div>
              </div>
            </div>
          )}
        </div>

        {/* Address */}
        {business.address && (
          <div className="mt-4 flex items-start gap-2 text-slate-600">
            <MapPin className="w-5 h-5 text-slate-400 mt-0.5" />
            <span>{business.address}</span>
          </div>
        )}

        {/* Contact Actions */}
        <div className="mt-6 flex flex-wrap gap-3">
          {business.phone && (
            <a
              href={`tel:${business.phone}`}
              className="flex items-center gap-2 px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors"
            >
              <Phone className="w-4 h-4" />
              {business.formatted_phone || business.phone}
            </a>
          )}
          
          {business.website && (
            <a
              href={business.website}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-colors"
            >
              <Globe className="w-4 h-4" />
              Web Sitesi
              <ExternalLink className="w-3 h-3" />
            </a>
          )}
          
          {business.google_maps_url && (
            <a
              href={business.google_maps_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-colors"
            >
              <MapPin className="w-4 h-4" />
              Google Maps
              <ExternalLink className="w-3 h-3" />
            </a>
          )}
        </div>
      </div>

      {/* Details Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Info Card */}
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h3 className="font-semibold text-slate-800 mb-4">Detaylar</h3>
          
          <div className="space-y-3">
            {business.city && (
              <div className="flex justify-between">
                <span className="text-slate-500">Şehir</span>
                <span className="text-slate-700">{business.city}</span>
              </div>
            )}
            {business.district && (
              <div className="flex justify-between">
                <span className="text-slate-500">İlçe</span>
                <span className="text-slate-700">{business.district}</span>
              </div>
            )}
            {business.postal_code && (
              <div className="flex justify-between">
                <span className="text-slate-500">Posta Kodu</span>
                <span className="text-slate-700">{business.postal_code}</span>
              </div>
            )}
            <div className="flex justify-between">
              <span className="text-slate-500">Koordinatlar</span>
              <span className="text-slate-700 text-sm">
                {business.latitude?.toFixed(6)}, {business.longitude?.toFixed(6)}
              </span>
            </div>
          </div>
        </div>

        {/* Opening Hours */}
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <Clock className="w-5 h-5 text-slate-400" />
            Çalışma Saatleri
          </h3>
          
          {business.opening_hours?.length > 0 ? (
            <div className="space-y-1 text-sm">
              {business.opening_hours.map((hour, index) => (
                <div key={index} className="text-slate-600">{hour}</div>
              ))}
            </div>
          ) : (
            <p className="text-slate-400 text-sm">Bilgi mevcut değil</p>
          )}
          
          {business.is_open_now !== null && (
            <div className={clsx(
              "mt-4 inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm",
              business.is_open_now 
                ? "bg-emerald-100 text-emerald-700"
                : "bg-red-100 text-red-700"
            )}>
              <span className={clsx(
                "w-2 h-2 rounded-full",
                business.is_open_now ? "bg-emerald-500" : "bg-red-500"
              )}></span>
              {business.is_open_now ? 'Şu an açık' : 'Şu an kapalı'}
            </div>
          )}
        </div>
      </div>

      {/* Tags */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <Tag className="w-5 h-5 text-slate-400" />
          Etiketler
        </h3>
        
        <div className="flex flex-wrap gap-2 mb-4">
          {business.tags?.map((tag) => (
            <span 
              key={tag}
              className="inline-flex items-center gap-1 bg-slate-100 text-slate-700 px-3 py-1 rounded-full text-sm group"
            >
              {tag}
              <button
                onClick={() => removeTagMutation.mutate(tag)}
                className="text-slate-400 hover:text-red-500 ml-1"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          ))}
          {(!business.tags || business.tags.length === 0) && (
            <span className="text-slate-400 text-sm">Henüz etiket eklenmedi</span>
          )}
        </div>
        
        <form onSubmit={handleAddTag} className="flex gap-2">
          <input
            type="text"
            value={newTag}
            onChange={(e) => setNewTag(e.target.value)}
            placeholder="Yeni etiket..."
            className="flex-1 px-3 py-1.5 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500"
          />
          <button
            type="submit"
            disabled={!newTag.trim() || addTagMutation.isPending}
            className="px-3 py-1.5 bg-primary-500 text-white rounded-lg text-sm hover:bg-primary-600 disabled:opacity-50"
          >
            <Plus className="w-4 h-4" />
          </button>
        </form>
      </div>

      {/* Notes */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-slate-800 flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-slate-400" />
            Notlar
          </h3>
          <button
            onClick={() => setShowAddNote(!showAddNote)}
            className="text-primary-600 hover:text-primary-700 text-sm font-medium"
          >
            + Not Ekle
          </button>
        </div>
        
        {showAddNote && (
          <form onSubmit={handleAddNote} className="mb-4">
            <textarea
              value={newNote}
              onChange={(e) => setNewNote(e.target.value)}
              placeholder="Notunuzu yazın..."
              rows={3}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 mb-2"
            />
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => {
                  setShowAddNote(false);
                  setNewNote('');
                }}
                className="px-3 py-1.5 text-slate-600 hover:bg-slate-100 rounded"
              >
                İptal
              </button>
              <button
                type="submit"
                disabled={!newNote.trim() || addNoteMutation.isPending}
                className="px-3 py-1.5 bg-primary-500 text-white rounded text-sm hover:bg-primary-600 disabled:opacity-50"
              >
                Kaydet
              </button>
            </div>
          </form>
        )}
        
        <div className="space-y-3">
          {business.notes?.map((note) => (
            <div key={note.id} className="bg-slate-50 rounded-lg p-3 group">
              <div className="flex justify-between items-start">
                <p className="text-slate-700 text-sm">{note.note}</p>
                <button
                  onClick={() => deleteNoteMutation.mutate(note.id)}
                  className="text-slate-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
              <div className="text-xs text-slate-400 mt-2">
                {new Date(note.created_at).toLocaleDateString('tr-TR', {
                  day: 'numeric',
                  month: 'long',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </div>
            </div>
          ))}
          {(!business.notes || business.notes.length === 0) && !showAddNote && (
            <p className="text-slate-400 text-sm">Henüz not eklenmedi</p>
          )}
        </div>
      </div>

      {/* Photos */}
      {business.photos?.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h3 className="font-semibold text-slate-800 mb-4">Fotoğraflar</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {business.photos.map((photo, index) => (
              <a 
                key={index}
                href={photo}
                target="_blank"
                rel="noopener noreferrer"
                className="aspect-square rounded-lg overflow-hidden bg-slate-100 hover:opacity-90 transition-opacity"
              >
                <img 
                  src={photo} 
                  alt={`${business.name} - ${index + 1}`}
                  className="w-full h-full object-cover"
                />
              </a>
            ))}
          </div>
        </div>
      )}

      {/* Danger Zone */}
      <div className="bg-white rounded-xl border border-red-200 p-6">
        <h3 className="font-semibold text-red-700 mb-2">Tehlikeli Bölge</h3>
        <p className="text-sm text-slate-500 mb-4">Bu işlemler geri alınamaz.</p>
        <button
          onClick={() => {
            if (window.confirm('Bu işletmeyi silmek istediğinizden emin misiniz?')) {
              deleteBusinessMutation.mutate();
            }
          }}
          disabled={deleteBusinessMutation.isPending}
          className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors disabled:opacity-50 flex items-center gap-2"
        >
          <Trash2 className="w-4 h-4" />
          İşletmeyi Sil
        </button>
      </div>
    </div>
  );
}

export default BusinessDetail;
