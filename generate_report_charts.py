"""
Generate high-resolution architecture diagrams and evaluation benchmark charts
for MannSahara Academic Project Report.
Outputs saved to docs/report_assets/
"""

import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

out_dir = Path("docs/report_assets")
out_dir.mkdir(parents=True, exist_ok=True)

# 1. Confusion Matrix (N=66)
fig, ax = plt.subplots(figsize=(6, 5), dpi=300)
cm = np.array([[23, 0], [0, 43]])
im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
ax.figure.colorbar(im, ax=ax)
ax.set(xticks=np.arange(cm.shape[1]),
       yticks=np.arange(cm.shape[0]),
       xticklabels=['Escalated (Crisis)', 'Non-Crisis (Support)'],
       yticklabels=['Actual Crisis', 'Actual Non-Crisis'],
       title='MannSahara Confusion Matrix (N=66)',
       ylabel='Ground Truth Intent',
       xlabel='System Classification / Action')

thresh = cm.max() / 2.
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        ax.text(j, i, format(cm[i, j], 'd'),
                ha="center", va="center",
                color="white" if cm[i, j] > thresh else "black",
                fontweight='bold', fontsize=14)
plt.tight_layout()
plt.savefig(out_dir / "fig_confusion_matrix.png", bbox_inches='tight')
plt.close()

# 2. Outcome Distribution Pie Chart
fig, ax = plt.subplots(figsize=(6, 5), dpi=300)
labels = ['True Negatives (43)', 'True Positives (23)']
sizes = [43, 23]
colors = ['#2B6CB0', '#319795']
explode = (0.04, 0.04)
wedges, texts, autotexts = ax.pie(sizes, 
                                  labels=labels, 
                                  autopct='%1.1f%%',
                                  startangle=140, 
                                  colors=colors, 
                                  explode=explode)
for at in autotexts:
    at.set_color('white')
    at.set_fontweight('bold')
ax.set_title('Classification Outcomes across 66 Synthetic Cases (100% Pass Rate)', fontsize=11, fontweight='bold', color='#1A365D')
plt.tight_layout()
plt.savefig(out_dir / "fig_outcome_distribution.png", bbox_inches='tight')
plt.close()

# 3. Category Pass Rates Bar Chart
fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
categories = ['Direct Crisis', 'Hinglish Crisis', 'Harmless Idioms', 'Veiled / Metaphorical', 'Academic Distress', 'Adversarial / Injection', 'Casual / Greetings']
rates = [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0]
bars = ax.barh(categories, rates, color='#2B6CB0', height=0.55)
ax.set_xlim(0, 115)
ax.set_xlabel('Benchmark Pass Rate (%)', fontweight='bold')
ax.set_title('Category-Specific Pass Rates (66 Synthetic Benchmark Cases - 100% Verified)', fontsize=11, fontweight='bold', color='#1A365D')
for bar in bars:
    w = bar.get_width()
    ax.text(w + 1.5, bar.get_y() + bar.get_height()/2, f'{w:.1f}%', va='center', fontweight='bold', fontsize=9, color='#2D3748')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(out_dir / "fig_category_performance.png", bbox_inches='tight')
plt.close()

# 4. Latency Profile Bar Chart
fig, ax = plt.subplots(figsize=(7, 4), dpi=300)
providers = ['Rules-Only (Local)', 'Gemini Cloud API', 'Ollama Qwen 1.5B (Local)', 'Ollama Qwen 3B (Local)']
latencies = [0.015, 1.18, 1.45, 3.82]
bars = ax.bar(providers, latencies, color=['#319795', '#805AD5', '#3182CE', '#2B6CB0'], width=0.5)
ax.set_ylabel('Inference Latency (Seconds)', fontweight='bold')
ax.set_title('Inference Latency Across Deployment Providers', fontsize=12, fontweight='bold', color='#1A365D')
for bar in bars:
    h = bar.get_height()
    label = f'{h*1000:.0f} ms' if h < 0.1 else f'{h:.2f} s'
    ax.text(bar.get_x() + bar.get_width()/2, h + 0.1, label, ha='center', fontweight='bold', fontsize=9)
ax.set_ylim(0, 4.5)
plt.tight_layout()
plt.savefig(out_dir / "fig_latency_profile.png", bbox_inches='tight')
plt.close()

# 5. System Architecture
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)
ax.axis('off')

ax.text(5, 5.6, "MannSahara End-to-End Multi-Tier System Architecture", 
        ha='center', va='center', fontsize=13, fontweight='bold', color='#1A365D')

def draw_box(ax, x, y, w, h, title, subtitle, color, text_color='white'):
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03", fc=color, ec="#4A5568", lw=1.2)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h*0.65, title, ha='center', va='center', fontsize=9.5, fontweight='bold', color=text_color)
    ax.text(x + w/2, y + h*0.3, subtitle, ha='center', va='center', fontsize=8, color=text_color, style='italic')

def draw_arrow(ax, x1, y1, x2, y2, label=""):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->", color="#2D3748", lw=1.5))
    if label:
        ax.text((x1+x2)/2, (y1+y2)/2 + 0.12, label, ha='center', va='center', fontsize=8, fontweight='bold', color="#2B6CB0")

draw_box(ax, 0.5, 4.2, 2.5, 0.9, "Student Client", "React 18 + Tailwind SPA", "#2B6CB0")
draw_box(ax, 3.8, 4.2, 2.5, 0.9, "API Gateway", "FastAPI Asynchronous REST", "#4A5568")
draw_box(ax, 7.0, 4.2, 2.5, 0.9, "Layer 1: Rules Engine", "Typo-Resilient Regex & Idioms", "#C53030")

draw_arrow(ax, 3.0, 4.65, 3.8, 4.65, "HTTPS /chat")
draw_arrow(ax, 6.3, 4.65, 7.0, 4.65, "Intake Text")

draw_box(ax, 7.0, 2.6, 2.5, 0.9, "Layer 2: LLM Classifier", "Zero-Shot Context Triage", "#2C7A7B")
draw_arrow(ax, 8.25, 4.2, 8.25, 3.5, "Ambiguous")

draw_box(ax, 3.5, 1.8, 3.0, 1.1, "LangGraph State Engine", "Finite-State Dynamic Router\nSticky Safety Lock", "#1A365D")
draw_arrow(ax, 7.0, 2.9, 6.5, 2.35, "Level 0-3")
draw_arrow(ax, 7.0, 4.4, 6.0, 2.9, "Forced L3")

draw_box(ax, 0.5, 1.8, 2.3, 1.0, "Output Validator", "Banned Tokens & Fallbacks", "#D69E2E", text_color="#1A202C")
draw_arrow(ax, 3.5, 2.3, 2.8, 2.3)
draw_arrow(ax, 1.65, 2.8, 1.65, 4.2, "Validated Reply")

draw_box(ax, 3.5, 0.3, 3.0, 0.8, "Local Persistence", "SQLite3 (mannsahara.db)", "#718096")
draw_arrow(ax, 5.0, 1.8, 5.0, 1.1, "Turn Store")

draw_box(ax, 7.0, 0.3, 2.5, 0.8, "Indian Crisis Helplines", "Tele-MANAS & 112 Cards", "#9B2C2C")
draw_arrow(ax, 6.5, 2.0, 7.5, 1.1, "Emergency Referral")

plt.tight_layout()
plt.savefig(out_dir / "fig_system_architecture.png", bbox_inches='tight')
plt.close()

# 6. LangGraph Flowchart
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)
ax.axis('off')

ax.text(5, 5.6, "MannSahara LangGraph Stateful Routing Engine", 
        ha='center', va='center', fontsize=13, fontweight='bold', color='#1A365D')

draw_box(ax, 4.0, 4.4, 2.0, 0.8, "START / assess", "Assess Risk Level", "#1A365D")
draw_box(ax, 0.5, 2.8, 2.0, 0.8, "crisis Node", "Template + Lock", "#9B2C2C")
draw_box(ax, 2.8, 2.8, 2.0, 0.8, "checkin Node", "Safety Question", "#D69E2E", text_color="#1A202C")
draw_box(ax, 5.2, 2.8, 2.0, 0.8, "support Node", "Empathetic LLM", "#2B6CB0")
draw_box(ax, 7.5, 2.8, 2.0, 0.8, "safety_followup", "Locked Safety LLM", "#742A2A")

draw_arrow(ax, 4.3, 4.4, 1.5, 3.6, "Level 3")
draw_arrow(ax, 4.8, 4.4, 3.8, 3.6, "Level 2")
draw_arrow(ax, 5.2, 4.4, 6.2, 3.6, "Level 0/1")
draw_arrow(ax, 5.8, 4.4, 8.5, 3.6, "Locked=True")

draw_box(ax, 4.0, 1.2, 2.0, 0.8, "validate Node", "Rule Guardrail Check", "#2C7A7B")
draw_arrow(ax, 6.2, 2.8, 5.5, 2.0)
draw_arrow(ax, 8.5, 2.8, 5.8, 2.0)

draw_box(ax, 4.0, 0.1, 2.0, 0.6, "END", "Client Delivery", "#4A5568")
draw_arrow(ax, 1.5, 2.8, 4.0, 0.4, "Pre-Approved")
draw_arrow(ax, 3.8, 2.8, 4.5, 0.7, "Pre-Approved")
draw_arrow(ax, 5.0, 1.2, 5.0, 0.7, "Passed")

plt.tight_layout()
plt.savefig(out_dir / "fig_langgraph_flowchart.png", bbox_inches='tight')
plt.close()

print("All report charts generated successfully in docs/report_assets/!")
