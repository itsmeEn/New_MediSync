<template>
  <div class="terms-page">
    <div class="terms-card">
      <div class="terms-header">
        <h1>Terms and Conditions</h1>
        <p class="subtitle">Please read all sections carefully before agreeing.</p>
      </div>

      <div ref="scrollBox" class="terms-content" @scroll="onScroll">
        <!-- Acceptance of Terms -->
        <section class="section" id="acceptance">
          <h5>Acceptance of Terms</h5>
          <p>
            By accessing or using MediSync, you agree to be bound by these Terms and Conditions
            and our Privacy Policy. If you do not agree, you must not use the platform.
          </p>
          <p>
            These terms may be updated from time to time. Continued use after changes constitute
            acceptance of the updated Terms.
          </p>
        </section>

        <!-- User Obligations -->
        <section class="section" id="user-obligations">
          <h5>User Accounts and Obligations</h5>
          <p>
            You are responsible for maintaining the confidentiality of your account credentials
            and for all activities under your account. You must provide accurate, current, and
            complete information and promptly update it when necessary.
          </p>
          <ul>
            <li>Use the platform in compliance with applicable laws and institutional policies.</li>
            <li>Do not share accounts or impersonate others.</li>
            <li>Report suspected security incidents promptly.</li>
          </ul>
        </section>

        <!-- Privacy and Data -->
        <section class="section" id="privacy-data">
          <h5>Privacy, Data Collection, and Processing</h5>
          <p>
            We collect data from user-submitted forms, device information, appointment
            interactions, and clinical entries recorded by authorized personnel. This includes
            patient demographics, vitals, assessments, medication records, audit logs, and
            operational events. Some data may be collected automatically for reliability and
            performance monitoring.
          </p>
          <p>
            Collected information is used for care delivery, decision support, scheduling,
            queue management, reporting, and service improvement. Role-based access controls and
            audit logging are enforced. Aggregated analytics may be used to improve systems
            without revealing identifiable patient details unless required by law or explicit
            consent.
          </p>
        </section>

        <!-- Patient Consent -->
        <section class="section" id="patient-consent">
          <h5>Patient Consent</h5>
          <p>
            By agreeing, patients consent to the collection and use of their health data to
            facilitate clinical services, scheduling, and health monitoring consistent with
            applicable regulations. Patients may request access to their records and withdraw
            consent where permitted by law.
          </p>
        </section>

        <!-- Allied Healthcare Policies -->
        <section class="section" id="allied-policies">
          <h5>Allied Healthcare Professional Policies</h5>
          <p>
            Allied health professionals must follow institutional policies and legal
            requirements when entering and accessing patient information. All entries should be
            accurate, timely, and attributable. Misuse of data or unauthorized access is
            strictly prohibited and subject to disciplinary action.
          </p>
          <div class="ai-highlight">
            <strong>AI & Predictive Analytics:</strong>
            Data may be used by AI models to forecast health trends, identify potential patient
            surges, and provide decision support. These models assist but do not replace clinical
            judgment. Recommendations should be contextualized by trained professionals.
          </div>
        </section>

        <!-- Intellectual Property -->
        <section class="section" id="ip">
          <h5>Intellectual Property</h5>
          <p>
            MediSync and its content, features, and functionality are owned by their respective
            rights holders and are protected by intellectual property laws. You may not copy,
            modify, distribute, or create derivative works without prior written permission.
          </p>
        </section>

        <!-- Prohibited Conduct -->
        <section class="section" id="prohibited">
          <h5>Prohibited Conduct</h5>
          <ul>
            <li>Attempt to gain unauthorized access to systems or data.</li>
            <li>Introduce malware or perform actions that disrupt operations.</li>
            <li>Use patient data for non-clinical or non-authorized purposes.</li>
          </ul>
        </section>

        <!-- Security -->
        <section class="section" id="security">
          <h5>Security</h5>
          <p>
            We implement safeguards to protect data, including encryption, access controls, and
            monitoring. No method of transmission or storage is 100% secure; users should employ
            best practices and report incidents immediately.
          </p>
        </section>

        <!-- Liability & Disclaimers -->
        <section class="section" id="liability">
          <h5>Limitations of Liability and Disclaimers</h5>
          <p>
            To the maximum extent permitted by law, MediSync and its affiliates are not liable
            for indirect, incidental, special, consequential, or punitive damages, or for loss of
            data, profits, or business arising from use of the platform.
          </p>
          <p>
            The platform is provided on an “as is” and “as available” basis. Clinical decisions
            remain the responsibility of qualified professionals.
          </p>
        </section>

        <!-- Indemnification -->
        <section class="section" id="indemnification">
          <h5>Indemnification</h5>
          <p>
            You agree to indemnify and hold harmless MediSync and its affiliates from claims,
            damages, liabilities, and expenses arising out of your use of the platform or breach
            of these terms.
          </p>
        </section>

        <!-- Termination and Changes -->
        <section class="section" id="termination">
          <h5>Termination</h5>
          <p>
            We may suspend or terminate access if you violate these terms or applicable laws.
          </p>
        </section>

        <section class="section" id="changes">
          <h5>Changes to Terms</h5>
          <p>
            We may revise these Terms periodically. Material changes will be communicated via the
            platform. Your continued use after changes indicates acceptance.
          </p>
        </section>

        <!-- Governing Law and Contact -->
        <section class="section" id="governing-law">
          <h5>Governing Law</h5>
          <p>
            These Terms are governed by the laws applicable to the organization operating
            MediSync, without regard to conflict of law principles.
          </p>
        </section>

        <section class="section" id="contact">
          <h5>Contact</h5>
          <p>
            For questions or requests regarding these Terms, please contact your system
            administrator or compliance officer.
          </p>
        </section>
      </div>

      <div class="terms-actions">
        <button v-if="showAccept" class="agree-btn" :disabled="!canAccept" @click="acceptTerms">
          I Agree
        </button>
        <button class="back-link" @click="goBack">Back to Login</button>
        <div class="scroll-hint" v-if="!showAccept">Scroll to the bottom to agree</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';

const router = useRouter();
const $q = useQuasar();
const scrollBox = ref<HTMLElement | null>(null);
const showAccept = ref(false);
const canAccept = ref(false);

const onScroll = () => {
  const el = scrollBox.value;
  if (!el) return;
  const atBottom = Math.ceil(el.scrollTop + el.clientHeight) >= el.scrollHeight;
  showAccept.value = atBottom;
  canAccept.value = atBottom;
};

const acceptTerms = () => {
  localStorage.setItem('termsAccepted', 'true');
  $q.notify({ type: 'positive', message: 'Terms accepted', timeout: 1500, position: 'top' });
  void router.push('/login');
};

const goBack = () => {
  void router.push('/login');
};

onMounted(() => {
  // Ensure top position and smooth behavior
  window.scrollTo({ top: 0, behavior: 'smooth' });
  // Focus the scrollable container
  if (scrollBox.value) {
    scrollBox.value.scrollTop = 0;
  }
});
</script>

<style scoped>
.terms-page {
  position: relative;
  padding: 24px;
  min-height: 100vh;
  display: flex;
  align-items: center; /* vertical centering */
  justify-content: center; /* horizontal centering */
}

/* Frosted glass background within the page container */
.terms-page::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(1200px 600px at 10% 10%, rgba(40, 102, 96, 0.14), transparent 60%),
              radial-gradient(1000px 500px at 90% 20%, rgba(108, 162, 153, 0.12), transparent 60%),
              linear-gradient(135deg, rgba(255,255,255,0.35) 0%, rgba(248,249,250,0.25) 50%, rgba(240,242,245,0.2) 100%);
  filter: saturate(120%);
  z-index: 0;
}

.terms-card {
  position: relative;
  z-index: 1;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.95);
  box-shadow:
    0 20px 40px rgba(0, 0, 0, 0.15),
    0 8px 16px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  overflow: hidden;
  width: 100%;
  max-width: 980px; /* keep a readable width */
}

.terms-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #286660, #6ca299, #b8d2ce);
}

.terms-header h1 {
  margin: 0 0 6px;
  font-size: 40px;
  font-weight: 700;
}
.terms-header {
  padding: 24px 24px 0; /* keep title away from card edges */
}

.terms-content {
  padding: 32px; /* increased indentation from card edges */
  height: 60vh;
  overflow-y: auto;
  font-size: 24px;
  line-height: 1.5;
}
.terms-content ul {
  padding-left: 28px; /* proper list indentation */
}
.terms-content p,
.terms-content li {
  text-align: justify; /* justify all body text */
  text-justify: inter-word;
}
.terms-content h5 {
  margin-top: 16px;
  font-weight: 700;
}
.section {
  margin-bottom: 18px;
}
.subtitle {
  margin: 0;
  color: #666;
  font-size: 16px;
}
.ai-highlight {
  margin-top: 8px;
  padding: 12px;
  border-left: 4px solid rgba(40, 102, 96, 0.8);
  background: rgba(242, 248, 247, 0.7);
}
.terms-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-top: 1px solid #eee;
}
.agree-btn {
  width: 200px;
  padding: 12px;
  background: #1e7668;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
}
.agree-btn:hover:not(:disabled) {
  background: #6ca299;
}
.agree-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}
.back-link {
  background: none;
  border: none;
  color: #1e7668;
  cursor: pointer;
  font-size: 14px;
  text-decoration: underline;
}
.scroll-hint {
  margin-left: auto;
  color: #666;
  font-size: 14px;
}

@media (max-width: 768px) {
  .terms-page {
    padding: 12px;
  }
  .terms-content {
    height: 58vh;
    padding: 20px; /* slightly reduced but still indented on mobile */
  }
  .agree-btn {
    width: 100%;
  }
  .back-link {
    font-size: 13px;
  }
}
</style>