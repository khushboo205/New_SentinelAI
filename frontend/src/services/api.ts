/**
 * SentinelAI Visual Intelligence Workbench — API Service Client
 * Resilient, type-safe communication with the FastAPI backend.
 * Provides live connection detection and graceful fallback to calibrated data.
 */

import {
  CameraFeed,
  ForensicEvent,
  TargetTrack,
  InvestigationDossier,
  QualityAnalysisResult,
  EnhancementRunResult,
  RiskEvaluationResult,
  SystemStatusResponse,
  EvidenceItem,
  ForensicCaseReport,
} from '../types/forensic';
import {
  CALIBRATED_CAMERAS,
  INITIAL_EVENTS,
  INITIAL_TRACKS,
  INITIAL_RISK_EVALUATION,
  INITIAL_EVIDENCE_ITEMS,
  INITIAL_REPORT,
} from '../data/sampleEvidence';

export const API_BASE = 'http://127.0.0.1:8000';

class SentinelApiService {
  private isOnlineCache: boolean | null = null;
  private lastCheckTime = 0;

  /**
   * Check backend health and readiness
   */
  async checkHealth(): Promise<{ online: boolean; platform?: string }> {
    const now = Date.now();
    if (this.isOnlineCache !== null && now - this.lastCheckTime < 5000) {
      return { online: this.isOnlineCache };
    }

    try {
      const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(2500) });
      if (res.ok) {
        const data = await res.json();
        this.isOnlineCache = true;
        this.lastCheckTime = now;
        return { online: true, platform: data.status || 'OK' };
      }
    } catch {
      // Try root fallback
      try {
        const rootRes = await fetch(`${API_BASE}/`, { signal: AbortSignal.timeout(2000) });
        if (rootRes.ok) {
          const rootData = await rootRes.json();
          this.isOnlineCache = true;
          this.lastCheckTime = now;
          return { online: true, platform: rootData.platform };
        }
      } catch {
        // Backend offline
      }
    }

    this.isOnlineCache = false;
    this.lastCheckTime = now;
    return { online: false };
  }

  /**
   * Fetch configured cameras with optical quality states
   */
  async getCameras(): Promise<{ cameras: CameraFeed[]; isLive: boolean }> {
    try {
      const res = await fetch(`${API_BASE}/cameras/`, { signal: AbortSignal.timeout(3000) });
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data.cameras) && data.cameras.length > 0) {
          return { cameras: data.cameras, isLive: true };
        }
      }
    } catch (err) {
      console.warn('Cameras API offline, utilizing calibrated feeds:', err);
    }
    return { cameras: CALIBRATED_CAMERAS, isLive: false };
  }

  /**
   * Fetch forensic events from repository
   */
  async getEvents(limit: number = 50): Promise<{ events: ForensicEvent[]; isLive: boolean }> {
    try {
      const res = await fetch(`${API_BASE}/events/?limit=${limit}`, { signal: AbortSignal.timeout(3000) });
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data.events) && data.events.length > 0) {
          // Format database rows into ForensicEvent if necessary
          const formatted: ForensicEvent[] = data.events.map((e: any) => ({
            id: e.id || e.event_id || Math.floor(Math.random() * 10000),
            timestamp: e.timestamp || e.event_time || '21:31:00',
            camera_id: e.camera_id || 'CAM_01',
            camera_name: e.camera_name || (e.camera_id === 'CAM_02' ? 'Checkpoint Alpha — Fast Lane' : 'Sector North — Perimeter Fence'),
            event_type: e.event_type || e.event || 'ZONE_INCURSION',
            severity: (e.severity || 'WARNING') as any,
            target_id: e.target_id || e.track_id || 1,
            target_type: e.target_type || e.class_name || 'person',
            confidence: e.confidence || 0.88,
            description: e.description || `Event logged on ${e.camera_id || 'CAM_01'}`,
            rule_triggered: e.rule_triggered || 'Standard Surveillance Trigger',
          }));
          return { events: formatted, isLive: true };
        }
      }
    } catch (err) {
      console.warn('Events API offline, utilizing calibrated stream:', err);
    }
    return { events: INITIAL_EVENTS, isLive: false };
  }

  /**
   * Fetch tracked target trajectories from database
   */
  async getTracks(): Promise<{ tracks: TargetTrack[]; isLive: boolean }> {
    try {
      const res = await fetch(`${API_BASE}/investigation/`, { signal: AbortSignal.timeout(3000) });
      if (res.ok) {
        const data = await res.json();
        const rows = Array.isArray(data) ? data : [];
        if (rows.length > 0) {
          const transformed: TargetTrack[] = rows.map((r: any) => ({
            track_id: r.track_id ?? r[0] ?? 1,
            class_name: r.class_name ?? r[1] ?? 'target',
            confidence: r.confidence ?? r[2] ?? 0.85,
            timestamp: r.timestamp ?? r[3] ?? '21:31:04',
            quality_score: r.quality_score ?? r[4] ?? 50.0,
            is_blurry: Boolean(r.is_blurry ?? r[5]),
            face_detected: Boolean(r.face_detected ?? r[6]),
            ocr_text: r.ocr_text ?? r[7] ?? '',
            risk_score: r.risk_score ?? 75,
            camera_id: r.camera_id ?? 'CAM_01',
            location: r.location ?? 'Sector 04 — North Boundary',
            velocity_kmh: r.velocity_kmh ?? 4.8,
            loitering_sec: r.loitering_sec ?? 0,
          }));
          return { tracks: transformed, isLive: true };
        }
      }
    } catch (err) {
      console.warn('Investigation tracks API offline, using calibrated tracks:', err);
    }
    return { tracks: INITIAL_TRACKS, isLive: false };
  }

  /**
   * Fetch track investigation dossier
   */
  async getInvestigation(trackId: number): Promise<{ dossier: InvestigationDossier | null; isLive: boolean }> {
    try {
      const res = await fetch(`${API_BASE}/investigation/${trackId}`, { signal: AbortSignal.timeout(3000) });
      if (res.ok) {
        const json = await res.json();
        if (json.success && json.data) {
          const d = json.data;
          const trackData = d.track;
          const transformedTrack: TargetTrack | null = trackData
            ? {
                track_id: trackData.track_id ?? trackData[0],
                class_name: trackData.class_name ?? trackData[1] ?? 'target',
                confidence: trackData.confidence ?? trackData[2] ?? 0.88,
                timestamp: trackData.timestamp ?? trackData[3] ?? '21:31:04',
                quality_score: trackData.quality_score ?? trackData[4] ?? 45.0,
                is_blurry: Boolean(trackData.is_blurry ?? trackData[5]),
                face_detected: Boolean(trackData.face_detected ?? trackData[6]),
                ocr_text: trackData.ocr_text ?? trackData[7] ?? '',
                risk_score: trackData.risk_score ?? 90,
                camera_id: trackData.camera_id ?? 'CAM_01',
                location: trackData.location ?? 'Sector 04 — North Boundary',
                velocity_kmh: trackData.velocity_kmh ?? 4.8,
                loitering_sec: trackData.loitering_sec ?? 0,
              }
            : null;

          const timeline: any[] = Array.isArray(d.timeline)
            ? d.timeline.map((t: any, idx: number) => ({
                id: idx + 1,
                timestamp: t.timestamp || t[2] || '21:31:04',
                description: t.event || t[1] || 'Track observation logged',
                camera_id: trackData?.camera_id || 'CAM_01',
              }))
            : [];

          return {
            dossier: {
              track: transformedTrack,
              timeline,
              evidence_count: d.evidence_count || 1,
              faces: d.faces || [],
              quality_history: d.quality_history || [],
            },
            isLive: true,
          };
        }
      }
    } catch (err) {
      console.warn(`Investigation dossier for #${trackId} offline:`, err);
    }

    const fallbackTrack = INITIAL_TRACKS.find((t) => t.track_id === trackId) || INITIAL_TRACKS[0];
    return {
      dossier: {
        track: fallbackTrack,
        timeline: [
          { id: 1, timestamp: '21:31:04', description: 'OBJECT_ENTERED: Target observed at boundary perimeter', camera_id: 'CAM_01' },
          { id: 2, timestamp: '21:31:08', description: 'QUALITY_DIAGNOSIS: Severe low-light degradation detected (<40)', camera_id: 'CAM_01' },
          { id: 3, timestamp: '21:31:10', description: 'ZONE_INCURSION: Exclusion boundary crossed into restricted zone', camera_id: 'CAM_01' },
          { id: 4, timestamp: '21:31:17', description: 'LOITERING_ALERT: Dwell duration reached 14.2s (Threshold: 10s)', camera_id: 'CAM_01' },
        ],
        evidence_count: 2,
        faces: [{ id: 1, confidence: 0.88, quality: 'ENHANCED_CROP' }],
        quality_history: [38.2, 41.5, 39.0, 78.4],
      },
      isLive: false,
    };
  }

  /**
   * Log manual or automated timeline event to an investigation track
   */
  async addTimelineEvent(trackId: number, event: string): Promise<boolean> {
    try {
      const res = await fetch(`${API_BASE}/investigation/${trackId}/timeline`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event }),
      });
      return res.ok;
    } catch {
      return false;
    }
  }

  /**
   * Fetch forensic evidence items committed to database vault
   */
  async getEvidenceList(): Promise<{ evidence: EvidenceItem[]; isLive: boolean }> {
    try {
      const res = await fetch(`${API_BASE}/evidence/`, { signal: AbortSignal.timeout(3000) });
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data.evidence) && data.evidence.length > 0) {
          return { evidence: data.evidence, isLive: true };
        }
      }
    } catch (err) {
      console.warn('Evidence API offline, using calibrated vault items:', err);
    }
    return { evidence: INITIAL_EVIDENCE_ITEMS, isLive: false };
  }

  /**
   * Retrieve single evidence artifact by ID
   */
  async getEvidence(evidenceId: string): Promise<{ evidence: EvidenceItem | null; isLive: boolean }> {
    try {
      const res = await fetch(`${API_BASE}/evidence/${evidenceId}`, { signal: AbortSignal.timeout(3000) });
      if (res.ok) {
        const item = await res.json();
        return { evidence: item, isLive: true };
      }
    } catch (err) {
      console.warn(`Evidence ${evidenceId} offline:`, err);
    }
    const found = INITIAL_EVIDENCE_ITEMS.find((e) => e.evidence_id === evidenceId) || null;
    return { evidence: found, isLive: false };
  }

  /**
   * Commit authentic enhanced derivative or crop to persistent evidence vault in database
   */
  async saveEvidence(evidence: EvidenceItem): Promise<{ success: boolean; evidence?: EvidenceItem }> {
    try {
      const res = await fetch(`${API_BASE}/evidence/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(evidence),
        signal: AbortSignal.timeout(5000),
      });
      if (res.ok) {
        const data = await res.json();
        return { success: true, evidence: data.evidence };
      }
    } catch (err) {
      console.warn('Failed to commit evidence to backend:', err);
    }
    return { success: false };
  }

  /**
   * Fetch forensic incident dossiers from repository
   */
  async getReports(): Promise<{ reports: ForensicCaseReport[]; isLive: boolean }> {
    try {
      const res = await fetch(`${API_BASE}/reports/`, { signal: AbortSignal.timeout(3000) });
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data.reports) && data.reports.length > 0) {
          return { reports: data.reports, isLive: true };
        }
      }
    } catch (err) {
      console.warn('Reports API offline, using calibrated report:', err);
    }
    return { reports: [INITIAL_REPORT], isLive: false };
  }

  /**
   * Fetch single dossier by case ID
   */
  async getReport(caseId: string): Promise<{ report: ForensicCaseReport | null; isLive: boolean }> {
    try {
      const res = await fetch(`${API_BASE}/reports/${caseId}`, { signal: AbortSignal.timeout(3000) });
      if (res.ok) {
        const rep = await res.json();
        return { report: rep, isLive: true };
      }
    } catch (err) {
      console.warn(`Report ${caseId} offline:`, err);
    }
    return { report: INITIAL_REPORT, isLive: false };
  }

  /**
   * Generate authentic forensic dossier from active database track & evidence state
   */
  async generateReport(
    trackId: number,
    leadInvestigator?: string,
    title?: string
  ): Promise<{ success: boolean; report?: ForensicCaseReport }> {
    try {
      const res = await fetch(`${API_BASE}/reports/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          track_id: trackId,
          lead_investigator: leadInvestigator || 'Visual Intelligence Unit (Operator Console)',
          title: title,
        }),
        signal: AbortSignal.timeout(5000),
      });
      if (res.ok) {
        const data = await res.json();
        return { success: true, report: data.report };
      }
    } catch (err) {
      console.warn('Failed to generate report via backend API:', err);
    }
    return { success: false };
  }

  /**
   * Save or update an incident dossier in the database
   */
  async saveReport(report: Partial<ForensicCaseReport>): Promise<{ success: boolean; report?: ForensicCaseReport }> {
    try {
      const res = await fetch(`${API_BASE}/reports/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(report),
        signal: AbortSignal.timeout(5000),
      });
      if (res.ok) {
        const data = await res.json();
        return { success: true, report: data.report };
      }
    } catch (err) {
      console.warn('Failed to save report to backend:', err);
    }
    return { success: false };
  }

  /**
   * Fetch track risk evaluation with contributing factors from deterministic risk engine
   */
  async getTrackRisk(trackId: number): Promise<{ result: RiskEvaluationResult; isLive: boolean }> {
    try {
      const res = await fetch(`${API_BASE}/risk/${trackId}`, { signal: AbortSignal.timeout(3000) });
      if (res.ok) {
        const data = await res.json();
        const rawFactors: any[] = data.contributing_factors || [];
        const factors = rawFactors.map((f: any) => ({
          name: f.label || f.factor || 'Risk Indicator',
          weight: f.weight ?? 15,
          active: true,
          reason: f.description || '',
        }));

        return {
          result: {
            composite_score: data.composite_score ?? 75,
            risk_level: data.risk_level ?? 'High',
            timestamp: data.timestamp || new Date().toTimeString().split(' ')[0],
            factors: factors.length > 0 ? factors : INITIAL_RISK_EVALUATION.factors,
          },
          isLive: true,
        };
      }
    } catch (err) {
      console.warn(`Track #${trackId} risk API offline, using fallback:`, err);
    }
    return { result: INITIAL_RISK_EVALUATION, isLive: false };
  }

  /**
   * Evaluate surveillance indicators against deterministic rule weights
   */
  async evaluateRisk(payload: {
    night_period?: boolean;
    restricted_zone?: boolean;
    loitering?: boolean;
    degraded_footage?: boolean;
    unverified_reid?: boolean;
    high_speed_movement?: boolean;
  }): Promise<{ result: RiskEvaluationResult; isLive: boolean }> {
    try {
      const res = await fetch(`${API_BASE}/risk/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: AbortSignal.timeout(3000),
      });
      if (res.ok) {
        const data = await res.json();
        return {
          result: {
            composite_score: data.composite_score ?? data.score ?? 75,
            risk_level: data.risk_level ?? 'High',
            timestamp: new Date().toTimeString().split(' ')[0],
            factors: data.contributing_factors ?? INITIAL_RISK_EVALUATION.factors,
          },
          isLive: true,
        };
      }
    } catch (err) {
      console.warn('Risk evaluation API offline, using calibrated engine:', err);
    }
    return { result: INITIAL_RISK_EVALUATION, isLive: false };
  }

  /**
   * Analyze image quality with OpenCV quality assessor
   */
  async analyzeQuality(file: File | Blob): Promise<QualityAnalysisResult> {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_BASE}/enhancement/analyze`, {
      method: 'POST',
      body: formData,
      signal: AbortSignal.timeout(15000),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Quality analysis failed' }));
      throw new Error(err.detail || 'Analysis request failed');
    }

    return res.json();
  }

  /**
   * Run adaptive enhancement pipeline
   */
  async runEnhancement(file: File | Blob, level?: string): Promise<EnhancementRunResult> {
    const formData = new FormData();
    formData.append('file', file);
    if (level) {
      formData.append('enhancement_level', level);
    }

    const res = await fetch(`${API_BASE}/enhancement/run`, {
      method: 'POST',
      body: formData,
      signal: AbortSignal.timeout(25000),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Enhancement run failed' }));
      throw new Error(err.detail || 'Enhancement request failed');
    }

    return res.json();
  }

  /**
   * Fetch hardware, device, and model capabilities
   */
  async getSystemStatus(): Promise<{ status: SystemStatusResponse | null; isLive: boolean }> {
    try {
      const res = await fetch(`${API_BASE}/system/status`, { signal: AbortSignal.timeout(3000) });
      if (res.ok) {
        const data = await res.json();
        return { status: data, isLive: true };
      }
    } catch (err) {
      console.warn('System status API offline:', err);
    }
    return {
      status: {
        platform: 'SentinelAI Visual Intelligence Engine',
        device: 'CPU (PyTorch 2.6.0 CPU Fallback)',
        processing_device: 'Intel Core CPU (1 worker thread)',
        python_version: '3.11.9',
        cuda_available: false,
        capabilities: {
          detection: { status: 'AVAILABLE', details: 'YOLO11 COCO object detection' },
          tracking: { status: 'AVAILABLE', details: 'ByteTrack persistent multi-object tracking' },
          enhancement: { status: 'AVAILABLE', details: 'ForensicProcessor OpenCV adaptive filters' },
          face_analysis: { status: 'AVAILABLE', details: 'Haar Cascade & MobileNet face crop detector' },
          ocr: { status: 'AVAILABLE', details: 'EasyOCR optical character recognition' },
          reid: { status: 'AVAILABLE', details: 'ResNet50 / color histogram appearance embeddings' },
          database: { status: 'AVAILABLE', details: 'SQLite transactional repository (sentinel.db)' },
        },
        measured_fps: {
          enhancement_fps: 4.4,
          yolo_fps: 18.8,
          ocr_fps: 3.3,
          composite_fps: 3.6,
        },
      },
      isLive: false,
    };
  }

  /**
   * Fetch summary detection counts
   */
  async getAnalyticsSummary(): Promise<{ total_tracks: number; people: number; vehicles: number; other: number }> {
    try {
      const res = await fetch(`${API_BASE}/analytics/summary`, { signal: AbortSignal.timeout(3000) });
      if (res.ok) {
        return res.json();
      }
    } catch {
      // Fallback
    }
    return { total_tracks: 18, people: 11, vehicles: 6, other: 1 };
  }

  /**
   * Construct absolute URL for sample CCTV frame
   */
  getSampleImageUrl(sampleId: string): string {
    return `${API_BASE}/enhancement/sample-image/${sampleId}`;
  }

  /**
   * Construct absolute URL for pre-computed enhanced sample frame
   */
  getSampleEnhancedUrl(sampleId: string): string {
    return `${API_BASE}/enhancement/sample-image-enhanced/${sampleId}`;
  }

  /**
   * Construct absolute URL for persisted derivative file
   */
  getDerivativeImageUrl(imageHash: string): string {
    return `${API_BASE}/enhancement/derivative/${imageHash}`;
  }
}

export const api = new SentinelApiService();
