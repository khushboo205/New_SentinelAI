/**
 * SentinelAI Visual Intelligence Workbench — Core Domain Types
 * Strict typing for optical quality analysis, adaptive enhancement,
 * target tracking, forensic event streams, and evidence provenance.
 */

export type NavWorkspace =
  | 'situation_room'
  | 'cameras'
  | 'live_monitoring'
  | 'analytics'
  | 'enhancement_lab'
  | 'events'
  | 'investigation'
  | 'evidence'
  | 'reports'
  | 'system_status'
  | 'security'
  | 'settings';

export type OperationalSeverity = 'NORMAL' | 'WATCH' | 'WARNING' | 'CRITICAL';
export type SystemMode = 'LIVE' | 'DEMO' | 'BENCHMARK';

export interface SurveillanceSettings {
  detectionConfidenceThreshold: number;
  iouThreshold: number;
  loiteringDwellTimeSec: number;
  speedAnomalyThresholdKmh: number;
  autoEnhanceDegradedThreshold: number;
  restrictedZoneWeight: number;
  nightMultiplier: number;
  audibleAlerts: boolean;
}

export interface CameraFeed {
  id: string;
  name: string;
  location: string;
  status: 'online' | 'offline' | 'degraded';
  stream_type: string;
  resolution: string;
  fps: number;
  quality_score: number;
  quality_label: 'NOMINAL' | 'ACCEPTABLE' | 'DEGRADED' | 'POOR';
  degradations: string[];
  recommended_pipeline: string[];
  active_targets: number;
  sample_id: 'lowlight' | 'blur' | 'fog' | 'raw';
  sample_url: string;
  last_activity: string;
  risk_level: 'Low' | 'Medium' | 'High' | 'Critical';
}

export interface QualityMetrics {
  blur_score: number;
  noise_score: number;
  brightness: number;
  contrast: number;
  dynamic_range: number;
  saturation: number;
  sharpness: number;
  motion_blur: number;
  compression_artifacts: number;
  resolution: [number, number];
  overall_quality: number;
}

export interface DiagnosisChip {
  label: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

export interface PipelineStep {
  op: string;
  label: string;
}

export interface QualityAnalysisResult {
  resolution: { width: number; height: number };
  metrics: QualityMetrics;
  overall_quality: number;
  quality_label: 'GOOD' | 'ACCEPTABLE' | 'DEGRADED' | 'POOR';
  diagnosis: DiagnosisChip[];
  should_enhance: boolean;
  enhancement_level: string;
  recommended_pipeline: PipelineStep[];
  assessor_diagnosis: string;
}

export interface EnhancedMediaArtifact {
  resolution: { width: number; height: number };
  quality_score: number;
  metrics: QualityMetrics;
  image_b64: string;
  integrity_hash: string;
  file_path: string;
  file_exists: boolean;
}

export interface EnhancementRunResult {
  status: 'enhanced' | 'unchanged';
  source: EnhancedMediaArtifact;
  output: EnhancedMediaArtifact;
  processing: {
    engine: string;
    level: string;
    pipeline_steps: PipelineStep[];
    processing_time_ms: number;
  };
  validation: {
    hash_changed: boolean;
    source_hash: string;
    output_hash: string;
    saved_to_disk: boolean;
    derivative_path: string;
    legal_notice: string;
  };
}

export interface TargetTrack {
  track_id: number;
  class_name: string;
  confidence: number;
  timestamp: string;
  quality_score: number;
  is_blurry: boolean;
  face_detected: boolean;
  ocr_text: string;
  risk_score?: number;
  camera_id?: string;
  location?: string;
  velocity_kmh?: number;
  loitering_sec?: number;
  reid_matched_tracks?: number[];
}

export interface TimelineEventRecord {
  id: number;
  timestamp: string;
  description: string;
  camera_id?: string;
}

export interface InvestigationDossier {
  track: TargetTrack | null;
  timeline: TimelineEventRecord[];
  evidence_count: number;
  faces: any[];
  quality_history: any[];
  reid_vector_preview?: string;
}

export interface ForensicEvent {
  id: number;
  timestamp: string;
  camera_id: string;
  camera_name: string;
  event_type: 'ZONE_INCURSION' | 'LOITERING' | 'SPEED_ANOMALY' | 'PLATE_DETECTED' | 'FACE_DETECTED' | 'DEGRADED_FEED' | 'DEGRADED_FOOTAGE';
  severity: OperationalSeverity;
  target_id: number;
  target_type: string;
  confidence: number;
  description: string;
  snapshot_url?: string;
  coordinates?: [number, number];
  rule_triggered: string;
}

export interface EvidenceItem {
  evidence_id: string;
  case_id: string;
  title: string;
  created_at: string;
  camera_id: string;
  source_type: 'RAW_FRAME' | 'ENHANCED_DERIVATIVE' | 'ANPR_CROP' | 'BIOMETRIC_CROP';
  original_hash: string;
  derivative_hash: string;
  processing_applied: string[];
  quality_delta_psnr: string;
  verified_by: string;
  classification: 'INTERNAL_VERIFICATION_HASH' | 'NON_CERTIFIED_OPERATIONAL_PREVIEW';
  source_image_url: string;
  enhanced_image_url?: string;
  notes: string;
}

export interface ForensicCaseReport {
  case_id: string;
  incident_title: string;
  incident_datetime: string;
  lead_investigator: string;
  location_sector: string;
  status: 'OPEN_INVESTIGATION' | 'PENDING_REVIEW' | 'CLOSED_RESOLVED';
  summary: string;
  primary_target_id: number;
  target_classification: string;
  evidence_items: EvidenceItem[];
  timeline: { time: string; event: string; camera: string }[];
  risk_score: number;
  risk_factors: string[];
  enhancement_log: { step: string; psnr_delta: string; duration_ms: number }[];
  integrity_seal_sha256: string;
}

export interface ControlledBenchmarkRecord {
  metric: string;
  before: number | string;
  after: number | string;
  delta: string;
  direction: 'improvement' | 'degradation' | 'neutral';
  explanation: string;
}

export interface RiskFactorBreakdown {
  name: string;
  weight: number;
  active: boolean;
  reason: string;
}

export interface RiskEvaluationResult {
  composite_score: number;
  risk_level: 'Low' | 'Medium' | 'High' | 'Critical';
  factors: RiskFactorBreakdown[];
  timestamp: string;
}

export interface CapabilityItem {
  status: 'AVAILABLE' | 'UNAVAILABLE';
  details: string;
  install_instructions?: string;
}

export interface SystemStatusResponse {
  platform: string;
  device: string;
  processing_device: string;
  python_version: string;
  cuda_available: boolean;
  capabilities: Record<string, CapabilityItem>;
  measured_fps: {
    enhancement_fps: number;
    yolo_fps: number;
    ocr_fps: number;
    composite_fps: number;
  };
}
