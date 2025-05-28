const fs = require('fs').promises;
const path = require('path');

/**
 * Document processor for legal documents
 * Handles text extraction, citation detection, and legal analysis
 */
class DocumentProcessor {
  constructor() {
    this.processingQueue = new Map();
  }

  /**
   * Process a legal document in the background
   * @param {string} documentId - Unique document identifier
   * @param {object} documentInfo - Document metadata and processing info
   */
  async processDocument(documentId, documentInfo) {
    try {
      console.log(`📄 Starting processing for document: ${documentId}`);
      
      // Update processing status
      this.processingQueue.set(documentId, {
        status: 'processing',
        startTime: new Date(),
        steps: {
          upload: { completed: true, timestamp: new Date() },
          textExtraction: { completed: false, progress: 0 },
          citationDetection: { completed: false, progress: 0 },
          vectorisation: { completed: false, progress: 0 }
        }
      });

      // Step 1: Extract text from document
      await this.extractText(documentId, documentInfo);
      
      // Step 2: Detect legal citations
      await this.detectCitations(documentId, documentInfo);
      
      // Step 3: Prepare for vectorisation (Week 2 Part 2)
      await this.prepareForVectorisation(documentId, documentInfo);
      
      // Mark as completed
      const processingInfo = this.processingQueue.get(documentId);
      processingInfo.status = 'completed';
      processingInfo.completedTime = new Date();
      
      console.log(`✅ Document processing completed: ${documentId}`);
      
    } catch (error) {
      console.error(`❌ Document processing failed for ${documentId}:`, error);
      
      const processingInfo = this.processingQueue.get(documentId);
      if (processingInfo) {
        processingInfo.status = 'failed';
        processingInfo.error = error.message;
      }
      
      throw error;
    }
  }

  /**
   * Extract text from uploaded document
   */
  async extractText(documentId, documentInfo) {
    console.log(`📝 Extracting text from: ${documentInfo.originalName}`);
    
    // Update progress
    const processingInfo = this.processingQueue.get(documentId);
    processingInfo.steps.textExtraction.progress = 50;
    
    // Simulate text extraction based on file type
    await this.simulateProcessingDelay(2000);
    
    let extractedText = '';
    
    switch (documentInfo.fileType) {
      case 'application/pdf':
        extractedText = await this.extractFromPdf(documentInfo);
        break;
      case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
      case 'application/msword':
        extractedText = await this.extractFromDocx(documentInfo);
        break;
      case 'text/plain':
        extractedText = await this.extractFromText(documentInfo);
        break;
      default:
        throw new Error(`Unsupported file type: ${documentInfo.fileType}`);
    }
    
    // Mark text extraction as completed
    processingInfo.steps.textExtraction.completed = true;
    processingInfo.steps.textExtraction.progress = 100;
    processingInfo.steps.textExtraction.timestamp = new Date();
    
    // Store extracted text (in production, this would go to database)
    processingInfo.extractedText = extractedText;
    
    console.log(`✅ Text extraction completed: ${extractedText.length} characters`);
  }

  /**
   * Detect legal citations in extracted text
   */
  async detectCitations(documentId, documentInfo) {
    console.log(`⚖️  Detecting legal citations in: ${documentInfo.originalName}`);
    
    const processingInfo = this.processingQueue.get(documentId);
    processingInfo.steps.citationDetection.progress = 25;
    
    await this.simulateProcessingDelay(1500);
    
    const extractedText = processingInfo.extractedText || '';
    const citations = this.findSouthAfricanCitations(extractedText);
    
    processingInfo.steps.citationDetection.progress = 75;
    await this.simulateProcessingDelay(1000);
    
    // Mark citation detection as completed
    processingInfo.steps.citationDetection.completed = true;
    processingInfo.steps.citationDetection.progress = 100;
    processingInfo.steps.citationDetection.timestamp = new Date();
    
    // Store detected citations
    processingInfo.citations = citations;
    
    console.log(`✅ Citation detection completed: ${citations.length} citations found`);
  }

  /**
   * Prepare document for vectorisation
   */
  async prepareForVectorisation(documentId, documentInfo) {
    console.log(`🔗 Preparing vectorisation for: ${documentInfo.originalName}`);
    
    const processingInfo = this.processingQueue.get(documentId);
    processingInfo.steps.vectorisation.progress = 50;
    
    await this.simulateProcessingDelay(1000);
    
    // Mark vectorisation as completed
    processingInfo.steps.vectorisation.completed = true;
    processingInfo.steps.vectorisation.progress = 100;
    processingInfo.steps.vectorisation.timestamp = new Date();
    
    console.log(`✅ Vectorisation preparation completed`);
  }

  /**
   * Find South African legal citations using regex patterns
   */
  findSouthAfricanCitations(text) {
    const citations = [];
    
    // South African citation patterns
    const patterns = [
      // Case law: 2019 (2) SA 343 (SCA)
      /\d{4}\s*\(\d+\)\s*SA\s+\d+\s*\([A-Z]+\)/g,
      // Constitutional Court: [2021] ZACC 13
      /\[\d{4}\]\s*ZACC\s+\d+/g,
      // Supreme Court of Appeal: [2020] ZASCA 99
      /\[\d{4}\]\s*ZASCA\s+\d+/g,
      // High Court: [2019] ZAGPPHC 123
      /\[\d{4}\]\s*ZA[A-Z]+HC\s+\d+/g,
      // BCLR citations: 2018 (7) BCLR 844
      /\d{4}\s*\(\d+\)\s*BCLR\s+\d+/g,
      // All SA citations: 1995 (3) SA 391 (CC)
      /\d{4}\s*\(\d+\)\s*SA\s+\d+\s*\([A-Z]+\)/g
    ];
    
    patterns.forEach(pattern => {
      const matches = text.match(pattern);
      if (matches) {
        matches.forEach(match => {
          citations.push({
            text: match.trim(),
            type: this.determineCitationType(match),
            jurisdiction: 'South Africa'
          });
        });
      }
    });
    
    // Remove duplicates
    return citations.filter((citation, index, self) => 
      index === self.findIndex(c => c.text === citation.text)
    );
  }

  /**
   * Determine the type of legal citation
   */
  determineCitationType(citation) {
    if (citation.includes('ZACC')) return 'Constitutional Court';
    if (citation.includes('ZASCA')) return 'Supreme Court of Appeal';
    if (citation.includes('HC')) return 'High Court';
    if (citation.includes('BCLR')) return 'BCLR Report';
    if (citation.includes('SA')) return 'South African Law Report';
    return 'Legal Citation';
  }

  /**
   * Mock text extraction methods (to be replaced with actual libraries in next step)
   */
  async extractFromPdf(documentInfo) {
    await this.simulateProcessingDelay(1000);
    return `Extracted text from PDF: ${documentInfo.originalName}\n\nThis is a mock legal document containing various South African case law references including 2019 (2) SA 343 (SCA) and [2021] ZACC 13. The document discusses constitutional matters and references the Companies Act 71 of 2008.`;
  }

  async extractFromDocx(documentInfo) {
    await this.simulateProcessingDelay(800);
    return `Extracted text from DOCX: ${documentInfo.originalName}\n\nLegal opinion regarding constitutional interpretation. Reference to [2020] ZASCA 99 and related cases. This document analyzes the application of 2018 (7) BCLR 844 in modern legal practice.`;
  }

  async extractFromText(documentInfo) {
    await this.simulateProcessingDelay(500);
    return `Plain text document: ${documentInfo.originalName}\n\nSimple legal text with citation 1995 (3) SA 391 (CC) and statutory reference to Constitution of the Republic of South Africa Act 108 of 1996.`;
  }

  /**
   * Get processing status for a document
   */
  getProcessingStatus(documentId) {
    return this.processingQueue.get(documentId) || null;
  }

  /**
   * Simulate processing delay for demonstration
   */
  async simulateProcessingDelay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Create singleton instance
const documentProcessor = new DocumentProcessor();

module.exports = documentProcessor;
