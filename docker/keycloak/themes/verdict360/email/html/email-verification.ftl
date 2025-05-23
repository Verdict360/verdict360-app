<#import "template.ftl" as layout>
<@layout.emailLayout>
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: #4F46E5; color: white; padding: 20px; text-align: center;">
        <h1 style="margin: 0;">Verdict360 Legal Platform</h1>
        <p style="margin: 5px 0 0 0;">Email Verification Required</p>
    </div>
    
    <div style="padding: 30px; background: #f9fafb;">
        <h2 style="color: #1E293B;">Verify Your Legal Account</h2>
        <p>Hello ${user.firstName!""},</p>
        <p>Welcome to Verdict360! To complete your registration and access the legal platform, please verify your email address.</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="${link}" style="background: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">Verify Email Address</a>
        </div>
        
        <p style="color: #6B7280; font-size: 14px;">This verification link will expire in ${linkExpiration}.</p>
        
        <div style="background: #FEF3C7; border: 1px solid #F59E0B; padding: 15px; border-radius: 6px; margin: 20px 0;">
            <p style="margin: 0; color: #92400E; font-size: 14px;"><strong>Security Notice:</strong> This platform handles confidential legal information. Only proceed if you created this account.</p>
        </div>
    </div>
    
    <div style="background: #1E293B; color: white; padding: 20px; text-align: center; font-size: 12px;">
        <p>&copy; ${.now?string("yyyy")} Verdict360. All rights reserved.</p>
        <p>This is an automated message from a secure legal platform.</p>
    </div>
</div>
</@layout.emailLayout>
