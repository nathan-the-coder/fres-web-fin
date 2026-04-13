
import { apiRequest } from '../core/api.js';

export async function generateReviewer(type, lesson, itemCount, userId = null) {
    const response = await apiRequest('/ai/generate', 'POST', {
        lesson_text: lesson,
        type,
        count: parseInt(itemCount, 10),
        user_id: userId,
    }, 2);

    if (!response.success) {
        throw new Error(response.error || "AI generation failed.");
    }

    return {
        questions: response.questions || "",
        answers: response.answers || "",
    };
}

export function handlePrint() {
    const q = localStorage.getItem('last_generated_q');
    const a = localStorage.getItem('last_generated_a');
    if (!q) return showToast("Generate a reviewer first!", "error");

    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>FRES Reviewer Export</title>
            <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;700;900&display=swap" rel="stylesheet">
            <style>
                body { font-family: 'Poppins', sans-serif; padding: 50px; line-height: 1.9; color: #1a1a1a; max-width: 800px; margin: 0 auto; }
                h1 { text-align: center; border-bottom: 4px solid #e91e63; padding-bottom: 12px; color: #e91e63; text-transform: uppercase; letter-spacing: 4px; font-size: 18pt; }
                .meta { text-align: center; font-size: 8pt; color: #888; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 30px; }
                .section-header { margin-top: 40px; font-weight: 900; color: #7b1fa2; border-left: 6px solid #e91e63; padding: 8px 15px; text-transform: uppercase; font-size: 10pt; letter-spacing: 3px; background: #fdf2f8; }
                .content { white-space: pre-wrap; margin-top: 20px; font-size: 11pt; line-height: 2; }
                @page { margin: 20mm; }
            </style>
        </head>
        <body>
            <h1>FRES WEB PORTAL</h1>
            <p class="meta">Generated: ${new Date().toLocaleString()} &nbsp;|&nbsp; Friendly Reviewer Educational System &nbsp;|&nbsp; NwSSU CCIS</p>
            <div class="section-header">📋 Practice Questions</div>
            <div class="content">${escapeHtml(q)}</div>
            <div class="section-header">✅ Answer Key</div>
            <div class="content">${escapeHtml(a)}</div>
        </body>
        </html>
    `);
    printWindow.document.close();
    printWindow.print();
}

export function downloadTXT() {
    const q = localStorage.getItem('last_generated_q');
    const a = localStorage.getItem('last_generated_a');
    if (!q) return showToast("Generate a reviewer first!", "error");

    const content = [
        "╔══════════════════════════════════════╗",
        "   FRES WEB ACADEMIC PORTAL - REVIEWER  ",
        "╚══════════════════════════════════════╝",
        `Generated: ${new Date().toLocaleString()}`,
        `System: Friendly Reviewer Educational System | NwSSU CCIS`,
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "QUESTIONS",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        q,
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "ANSWER KEY",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        a,
    ].join("\n");

    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `FRES_Reviewer_${Date.now()}.txt`;
    link.click();
    URL.revokeObjectURL(url);
}

function escapeHtml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// Toast helper (can be imported or used standalone)
function showToast(msg, type = "info") {
    const existing = document.getElementById('fres-toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.id = 'fres-toast';
    toast.style.cssText = `
        position: fixed; bottom: 24px; right: 24px; z-index: 9999;
        padding: 14px 24px; border-radius: 14px; font-size: 12px; font-weight: 700;
        letter-spacing: 1px; text-transform: uppercase; color: white;
        background: ${type === 'error' ? '#dc2626' : type === 'success' ? '#16a34a' : '#7c3aed'};
        box-shadow: 0 8px 32px rgba(0,0,0,0.4); animation: slideUp 0.3s ease;
    `;
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}
