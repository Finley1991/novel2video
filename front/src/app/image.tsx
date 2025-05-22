"use client"

import React, { useState, useEffect } from 'react';
import Image from "next/image";
import {showToast} from "@/app/toast";
import {ToastContainer, toast } from 'react-toastify'; // 确保导入 toast
import 'react-toastify/dist/ReactToastify.css'; // 确保导入 toastify CSS

// 按钮基础样式（可提取到组件顶部常量）
const buttonBaseStyle = {
    padding: '0.5rem 1rem',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '0.9rem',
    transition: 'all 0.2s ease',
    display: 'flex',
    alignItems: 'center'
};

// 主按钮样式（重要操作）
const buttonPrimaryStyle = {
    backgroundColor: '#2563eb',
    color: 'white',
    boxShadow: '0 1px 2px 0 rgba(0,0,0,0.05)'
};

// 次按钮样式（辅助操作）
const buttonSecondaryStyle = {
    backgroundColor: '#f3f4f6',
    color: '#111827'
};

// 轮廓按钮样式（刷新等轻操作）
const buttonOutlineStyle = {
    backgroundColor: 'transparent',
    color: '#2563eb',
    border: '1px solid #e5e7eb'
};

export default function AIImageGenerator() {
    const [images, setImages] = useState<string[]>([]);
    const [fragments, setFragments] = useState<string[]>([]);
    const [prompts, setPrompts] = useState<string[]>([]);
    const [loaded, setLoaded] = useState<boolean>(false);
    const [promptsEn, setPromptsEn] = useState<string[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(false); // Assuming you might want to use this
    const [audioPaths, setAudioPaths] = useState<string[]>([]);

    useEffect(() => {
        initialize();
    }, []);

    const addCacheBuster = (url: string) => {
        const cacheBuster = `?v=${Date.now()}`
        return url.includes('?') ? `${url}&${cacheBuster}` : `${url}${cacheBuster}`
  }

    const initialize = () => {
        fetch('http://localhost:8080/api/novel/initial')
            .then(response => response.json())
            .then(data => {
                setFragments(data.fragments || []);
                const updatedImages = (data.images || []).map((imageUrl: string) =>
                  addCacheBuster(`http://localhost:8080${imageUrl}`)
                )
                setImages(updatedImages);
                setPrompts(data.prompts || []);
                setPromptsEn(data.promptsEn || [])
                
                const numFragments = data.fragments?.length || 0;
                const newAudioPaths = Array(numFragments).fill(''); // Initialize with empty strings

                if (data.audioFiles && Array.isArray(data.audioFiles)) {
                    // Map provided audio paths to full URLs, extracting filename if necessary
                    const processedAudioFileUrls = data.audioFiles.map((audioPath: string | null) => {
                        if (audioPath) {
                            // Extract filename from the path (works for OS paths and URL paths)
                            const filename = audioPath.split(/[\\/]/).pop();
                            if (filename) {
                                return addCacheBuster(`http://localhost:8080/temp/audio/${filename}`);
                            }
                        }
                        return ''; // Return empty string if path is null, empty, or filename extraction fails
                    });

                    // Populate newAudioPaths, ensuring it matches numFragments length
                    for (let i = 0; i < numFragments; i++) {
                        if (i < processedAudioFileUrls.length) {
                            newAudioPaths[i] = processedAudioFileUrls[i];
                        }
                        // If i >= processedAudioFileUrls.length, newAudioPaths[i] remains '', which is correct.
                    }
                }
                setAudioPaths(newAudioPaths);
                setLoaded(true);
            })
            .catch(error => {
                console.error('Error initializing data:', error);
                setLoaded(false);
            });
    };

    const extractChapterFragments = () => {
        fetch('http://localhost:8080/api/get/novel/fragments')
            .then(response => response.json())
            .then(data => {
                setFragments(data);
                setImages(data.map(() => "http://localhost:8080/images/placeholder.png"));
                // 根据新的 fragments 长度初始化 audioPaths
                setAudioPaths(Array(data.length).fill(''));
                setLoaded(true);
            })
            .catch(error => {
                console.error('Error fetching file content:', error);
                setLoaded(false);
            });
    };

    const extractPrompts = () => {
        setPrompts([]);
        showToast('开始生成');
        fetch('http://localhost:8080/api/get/novel/prompts')
            .then(response => response.json())
            .then(data => {
            setPrompts(data || []);
            console.log('Prompts fetched successfully');
        })
        .catch(error => {
            console.error('Error fetching prompts:', error);
            showToast('失败');
        });
    };

    const generateAllImages = () => {
        setImages([]);
        showToast('开始生成，请等待');
        fetch('http://localhost:8080/api/novel/images', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
        })
            .then(response => response.json())
            .then(() => {
                console.log('Images generation initiated');
                refreshImages();
            })
            .catch(error => {
                showToast('失败，请检查日志');
                console.error('Error generating all images:', error)
            });
    };

    type ImageMap = Record<string, string>;

    const refreshImages = () => {
        fetch('http://localhost:8080/api/novel/images')
            .then(response => response.json() as Promise<ImageMap>)
            .then((imageMap: ImageMap) => {
                const updatedImages = [...images];
                for (const [index, imageUrl] of Object.entries(imageMap)) {
                    const numericIndex = Number(index);
                    if (!isNaN(numericIndex)) {
                        updatedImages[numericIndex] = addCacheBuster(`http://localhost:8080${imageUrl}`);
                    }
                }
                setImages(updatedImages);
            })
            .catch(error => console.error('Error fetching image:', error));
    };

    const mergeFragments = (index: number, direction: 'up' | 'down') => {
        if ((direction === 'up' && index === 0) || (direction === 'down' && index === fragments.length - 1)) {
            return;
        }

        const newFragments = [...fragments];
        const newImages = [...images];
        const newPrompts = [...prompts]
        const newPromptsEn = [...promptsEn]
        const newAudioPaths = [...audioPaths]; // 新增对 audioPaths 的处理

        if (direction === 'up') {
            newFragments[index - 1] += ' ' + newFragments[index];
            newFragments.splice(index, 1);
            newImages.splice(index, 1);
            newPrompts.splice(index, 1)
            newPromptsEn.splice(index, 1)
            newAudioPaths.splice(index, 1); // 同步删除 audioPath
        } else if (direction === 'down') {
            newFragments[index] += ' ' + newFragments[index + 1];
            newFragments.splice(index + 1, 1);
            newImages.splice(index + 1, 1);
            newPrompts.splice(index+1, 1)
            newPromptsEn.splice(index+1, 1)
            newAudioPaths.splice(index + 1, 1); // 同步删除 audioPath
        }

        setFragments(newFragments);
        setImages(newImages);
        setPromptsEn(newPromptsEn); // 修正: 使用 newPromptsEn
        setPrompts(newPrompts);   // 修正: 使用 newPrompts
        setAudioPaths(newAudioPaths); // 设置新的 audioPaths
        // todo 是不是最好都重新保存一下
        saveFragments(newFragments);
    };

    const saveFragments = async (fragments: string[]) => {
        try {
            const response = await fetch('http://localhost:8080/api/save/novel/fragments', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(fragments),
            });

            if (!response.ok) {
                throw new Error('Failed to save fragments');
            }
            console.log('Fragments saved successfully');
        } catch (error) {
            console.error('Error saving fragments:', error);
        }
    };

    const generateSingleImage = async (index:number) => {
        try {
            showToast('开始');
            const updatedImages = [...images];
            updatedImages[index] = "http://localhost:8080/images/placeholder.png";
            const response = await fetch('http://localhost:8080/api/novel/image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    index: index,
                    content: promptsEn[index]
                }),
            });
            if (!response.ok) {
                throw new Error('Failed to regenerate image');
            }
            const data = await response.json();
            const imageUrl = data.url;
            updatedImages[index] = addCacheBuster(`http://localhost:8080${imageUrl}`);
            setImages(updatedImages);
            console.log(`successfully regenerate image for prompt ${index}.`);
            showToast('成功');
        } catch (error) {
            console.error('Error saving attachment:', error);
            showToast('失败');
        }
    }

    const generateSinglePromptZh = async (index: number, fragmentText: string) => {
        if (!fragmentText) {
            showToast('片段文本不能为空');
            return;
        }
        showToast(`开始为片段 ${index + 1} 生成中文Prompt`);
        try {
            const response = await fetch('http://localhost:8080/api/novel/prompt/zh/single', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: fragmentText, index: index }),
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || '生成中文Prompt失败');
            }
            const data = await response.json();
            const newPrompts = [...prompts];
            newPrompts[index] = data.prompt;
            setPrompts(newPrompts);
            showToast(`片段 ${index + 1} 中文Prompt生成成功`);
            savePromptZh(index, data.prompt); // Optionally auto-save
        } catch (error: any) {
            console.error('Error generating single Chinese prompt:', error);
            showToast(`生成中文Prompt失败: ${error.message}`);
        }
    };

    const translateSinglePromptEn = async (index: number, chinesePrompt: string) => {
        if (!chinesePrompt) {
            showToast('中文Prompt不能为空');
            return;
        }
        showToast(`开始为片段 ${index + 1} 翻译英文Prompt`);
        try {
            const response = await fetch('http://localhost:8080/api/novel/prompt/en/single', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: chinesePrompt, index: index }),
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || '翻译英文Prompt失败');
            }
            const data = await response.json();
            const newPromptsEn = [...promptsEn];
            newPromptsEn[index] = data.prompt_en;
            setPromptsEn(newPromptsEn);
            showToast(`片段 ${index + 1} 英文Prompt翻译成功`);
            savePromptEn(index, data.prompt_en); // Optionally auto-save
        } catch (error: any) {
            console.error('Error translating single prompt to English:', error);
            showToast(`翻译英文Prompt失败: ${error.message}`);
        }
    };

    const generateSingleAudio = async (index: number, textToSpeak: string) => {
        if (!textToSpeak) {
            showToast('用于生成语音的文本不能为空');
            return;
        }
        showToast(`开始为片段 ${index + 1} 生成语音`);
        try {
            const response = await fetch('http://localhost:8080/api/novel/audio/single', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: textToSpeak, index: index }),
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || '生成语音失败');
            }
            const data = await response.json(); // data.path 包含音频路径
            const newAudioPaths = [...audioPaths];
            // 确保使用 addCacheBuster 并拼接基础 URL
            const fullPathFromBackend = data.path;
            const filename = fullPathFromBackend.split(/[\\/]/).pop(); 
            if (!filename) {
                throw new Error('Invalid audio file path received from backend');
            }
            newAudioPaths[index] = addCacheBuster(`http://localhost:8080/temp/audio/${filename}`);
            setAudioPaths(newAudioPaths);
            showToast(`片段 ${index + 1} 语音生成成功`);
        } catch (error: any) {
            console.error('Error generating single audio:', error);
            showToast(`生成语音失败: ${error.message}`);
        }
    };

    // Modify existing savePromptZh and savePromptEn to accept content as parameter
    const savePromptZh = async (index: number, content?: string) => {
        const promptToSave = content !== undefined ? content : prompts[index];
        if (promptToSave === undefined) {
            showToast('没有可保存的中文Prompt');
            return;
        }
        try {
            const response = await fetch('http://localhost:8080/api/novel/prompt/zh', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    index: index,
                    content: promptToSave
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to save attachment');
            }
            console.log(`Attachment for fragment ${index + 1} saved successfully.`);
            showToast('保存成功');
        } catch (error) {
            console.error('Error saving attachment:', error);
            showToast('保存失败');
        }
    };

    const savePromptEn = async (index: number, content?: string) => {
        const promptEnToSave = content !== undefined ? content : promptsEn[index];
        if (promptEnToSave === undefined) {
            showToast('没有可保存的英文Prompt');
            return;
        }
        try {
             // ... (rest of the savePromptEn logic, using promptEnToSave)
            const response = await fetch('http://localhost:8080/api/novel/prompt/en', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    index: index,
                    content: promptEnToSave
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to save attachment');
            }
            console.log(`Attachment for fragment ${index + 1} saved successfully.`);
            showToast('保存成功');
        } catch (error) {
            console.error('Error saving attachment:', error);
            showToast('保存失败');
        }
    };

    const generatePromptsEn = async () => {
        try {
            setPromptsEn([]);
            showToast('开始生成，请等待');
            const response = await fetch('http://localhost:8080/api/novel/prompts/en');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            setPromptsEn(data || []);
        } catch (error) {
            showToast('失败');
            console.error('Error fetching prompts:', error);
        }
    };


    const generateAudio = () => {
        showToast('开始批量生成音频，请等待');
        // 注意：当前的 /api/novel/audio 接口可能需要根据 fragments 列表来确定生成哪些音频
        // 如果后端是根据已保存的 fragments 文件来生成，则不需要传递 body
        // 如果需要传递当前前端的 fragments，则需要修改 body
        fetch('http://localhost:8080/api/novel/audio', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            // body: JSON.stringify({ fragments }) // 如果后端需要当前片段列表
        })
            .then(response => response.json())
            .then(data => { // 假设后端返回 { paths: ["/tmp/audio/0.mp3", "/tmp/audio/1.mp3", ...] }
                if (data && data.paths && Array.isArray(data.paths)) {
                    const newAudioUrls = data.paths.map((relativePath: string) =>
                        relativePath ? addCacheBuster(`http://localhost:8080${relativePath}`) : ''
                    );
                    
                    // 将新的URL更新到audioPaths，保持与fragments长度一致
                    const finalAudioPaths = fragments.map((_, i) => newAudioUrls[i] || '');
                    setAudioPaths(finalAudioPaths);
                    showToast('所有音频生成完成!');
                    console.log('All audio generation completed and paths updated.');
                } else {
                    // 如果后端不返回路径，或者格式不符，可以尝试刷新所有音频路径
                    // 这依赖于 initialize 函数能够正确加载它们
                    // 或者，后端可以不返回路径，前端在成功后调用 initialize() 来刷新所有数据包括音频
                    console.warn('Backend did not return audio paths for batch generation, or format was unexpected. Consider refreshing.');
                    // 你可以选择在这里调用 initialize() 来刷新，或者提示用户手动刷新
                    // initialize(); // 可选：如果后端不返回路径，则重新初始化以获取
                    showToast('批量音频任务已发送，稍后请检查或刷新。');
                }
            })
            .catch(error => {
                console.error('Error generating all audio:', error);
                showToast('批量生成音频失败，请检查日志');
            });
    };

    return (
        <div className="container">
            {/* 优化后的顶部功能栏 */}
            <div className="header" style={{
                backgroundColor: '#f8f9fa',
                borderBottom: '1px solid #e9ecef',
                padding: '1rem 1.5rem',
                marginBottom: '1.5rem',
                borderRadius: '8px'
            }}>
                <div className="button-container" style={{
                    display: 'flex',
                    gap: '0.75rem',
                    flexWrap: 'wrap',
                    maxWidth: '1200px',
                    margin: '0 auto'
                }}>
                    {/* 基础按钮样式 */}
                    <button 
                        onClick={extractChapterFragments}
                        style={{...buttonBaseStyle, ...buttonPrimaryStyle}}
                        className="primary-btn"
                    >
                        分块
                    </button>
                    
                    {loaded && (
                        <>
                            <button 
                                onClick={extractPrompts} 
                                className="extract-prompts-button"
                                style={{...buttonBaseStyle, ...buttonPrimaryStyle}}
                            >
                                一键分镜
                            </button>
                            
                            <button 
                                onClick={generatePromptsEn} 
                                className="generate-promptsEn" 
                                disabled={isLoading}
                                style={{...buttonBaseStyle, ...buttonPrimaryStyle}}
                            >
                                {isLoading ? 'Generating...' : '一键翻译'}
                            </button>
                            
                            <button 
                                onClick={generateAllImages} 
                                className="generate-all"
                                style={{...buttonBaseStyle, ...buttonPrimaryStyle}}
                            >
                                一键作图
                            </button>
                            
                            <button 
                                onClick={initialize} 
                                className="refresh-images"
                                style={{...buttonBaseStyle, ...buttonOutlineStyle}}
                            >
                                刷新
                            </button>
                            
                            <button 
                                onClick={generateAudio} 
                                className="generate-audio"
                                style={{...buttonBaseStyle, ...buttonPrimaryStyle}}
                            >
                                一键音频
                            </button>
                        </>
                    )}
                </div>
            </div>
            
            {loaded && (
                <>
                    {fragments.map((line, index) => (
                        <div key={index} className="card">
                            <div className="input-section">
                                <textarea value={line} readOnly rows={4} className="scrollable"></textarea>
                                <div className="button-group">
                                    {index !== 0 && (
                                        <button className="merge-button" onClick={() => mergeFragments(index, 'up')}>向上合并</button>
                                    )}
                                    {index !== fragments.length - 1 && (
                                        <button className="merge-button" onClick={() => mergeFragments(index, 'down')}>向下合并</button>
                                    )}
                                    <button onClick={() => generateSinglePromptZh(index, line)} style={{marginTop: '5px'}}>分镜</button>
                                    {/* "生成语音(片段)" 按钮位置保持在 input-section 内，使其与片段内容关联更紧密 */}
                                    <button onClick={() => generateSingleAudio(index, line)} style={{marginTop: '5px'}}>语音</button>
                                </div>
                            </div>
                            <div className="prompt-section">
                                <textarea
                                    value={prompts[index] || ''}
                                    placeholder="中文 prompt"
                                    onChange={(e) => {
                                        const newAttachments = [...prompts];
                                        newAttachments[index] = e.target.value;
                                        setPrompts(newAttachments);
                                    }}
                                    rows={4}
                                    className="scrollable"
                                ></textarea>
                                <button onClick={() => savePromptZh(index)}>分镜保存</button>
                                <button onClick={() => translateSinglePromptEn(index, prompts[index])} style={{marginLeft: '5px'}}>绘图提示词</button>
                                {/* "生成语音(中文Prompt)" 按钮位置保持在 prompt-section 内，使其与中文Prompt内容关联更紧密 */}
                                {/* <button onClick={() => generateSingleAudio(index, prompts[index])} style={{marginTop: '5px'}}>生成语音(中文Prompt)</button> */}
                            </div>
                            <div className="promptEn-section">
                                <textarea
                                    value={promptsEn[index] || ''}
                                    onChange={(e) => {
                                        const newAttachments = [...promptsEn];
                                        newAttachments[index] = e.target.value;
                                        setPromptsEn(newAttachments);
                                    }}
                                    placeholder="英文 prompt"
                                    rows={4}
                                    className="scrollable"
                                ></textarea>
                                <button onClick={() => savePromptEn(index)}>提示词保存</button>
                                <button onClick={() => generateSingleImage(index)}>图片</button>
                            </div>
                            <div className="image-section">
                                <Image
                                    src={images[index]}
                                    key={images[index]} // 使用 images[index] 作为 key
                                    alt={`Generated image ${index + 1}`}
                                    width={300}
                                    height={200}
                                />
                                {/* 音频播放器放置在图片下方 */}
                                {audioPaths[index] && (
                                    <div className="mt-2">
                                        <p className="text-sm font-medium text-gray-700">语音:</p>
                                        <audio 
                                        controls 
                                        src={audioPaths[index]}

                                        className="w-full"
                                        // preload="metadata" // 可选，有助于加载音频元数据
                                        >
                                        你的浏览器不支持播放音频。
                                        </audio>
                                    </div>
                                    )}
                            </div>
                        </div>
                    ))}
                </>
            )}
            <style jsx>{`
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    font-family: Arial, sans-serif;
                    background-color: #f7f7f7;
                    color: #333;
                }
                .header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                }
                .button-container {
                    display: flex;
                    gap: 20px;
                    margin-bottom: 20px;
                }
                .card {
                    display: flex;
                    justify-content: space-between;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;
                    background-color: #fff;
                }
                .input-section, .prompt-section, .promptEn-section, .image-section {
                    width: 23%;
                    display: flex; /* Added for vertical alignment of content */
                    flex-direction: column; /* Stack items vertically */
                }
                textarea {
                    width: 100%;
                    padding: 10px;
                    margin-bottom: 10px; /* 统一 margin-bottom */
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    box-sizing: border-box;
                    min-height: 80px; /* 给予最小高度 */
                }
                .button-group {
                    display: flex;
                    flex-wrap: wrap; /* 允许按钮换行 */
                    gap: 5px; /* 按钮之间的间隙 */
                    margin-top: auto; /* Pushes button group to the bottom if section has extra space */
                }
                .button-group button, .prompt-section button, .promptEn-section button {
                    padding: 8px 12px; /* 统一按钮padding */
                    font-size: 0.9em; /* 统一按钮字体大小 */
                    cursor: pointer;
                    border: 1px solid #007bff;
                    background-color: #fff;
                    color: #007bff;
                    border-radius: 4px;
                    transition: background-color 0.2s, color 0.2s;
                }
                .button-group button:hover, .prompt-section button:hover, .promptEn-section button:hover {
                    background-color: #007bff;
                    color: white;
                }
                .image-section Image { /* Next.js Image component might not be styled directly like this */
                    display: block;
                    max-width: 100%;
                    height: auto; /* Maintain aspect ratio */
                    border-radius: 4px;
                    margin-bottom: 10px; /* Space between image and audio player */
                }
                .image-section audio {
                    width: 100%;
                    margin-top: 10px; /* 确保音频播放器和图片之间有间距 */
                }
                .scrollable {
                    overflow-y: auto;
                }

                /* Responsive adjustments */
                @media (max-width: 992px) {
                    .input-section, .prompt-section, .promptEn-section, .image-section {
                        flex-basis: 48%; /* Two columns on medium screens */
                    }
                }
                @media (max-width: 768px) {
                    .input-section, .prompt-section, .promptEn-section, .image-section {
                        flex-basis: 100%; /* Single column on small screens */
                    }
                    .button-container {
                        flex-direction: column; /* Stack header buttons on small screens */
                        gap: 8px;
                    }
                }
            `}</style>
            <ToastContainer />{/* This should be inside the main returned div */}
        </div>
    );
}
